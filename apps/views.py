from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Trunk
from .models import AmazonTransaction
from .models import Tracking, Warehouse
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core import serializers
from copy import deepcopy
from django.http import JsonResponse
from django.core import serializers
import json
# Create your views here.

# 0:created  1:trunk to warehouse  2:trunk waiting in warehouse 3:out for delivery
def intToStatus(num):
    if num == 0:
        return "created"
    elif num == 1:
        return "in the way to warehouse"
    elif num == 2:
        return "waiting for loading"
    elif num == 3:
        return "out for delivery"
    else:
        return "delivered"

def getStatus(tracking):
    if tracking.finished:
        return "delivered"
    elif not tracking.assigned_trunk:
        return "created"
    else:
        return intToStatus(Trunk.objects.get(trunk_id=tracking.trunk_id).status)

def home(request):
    trackings = []
    tracking_statuses = []
    for tracking in Tracking.objects.all():
        tracking.strStatus = getStatus(tracking)
        trackings.append(tracking)
    print(trackings)
    return render(request, "apps/all_list.html", {"trackings":trackings})

def tracking_detail(request, key):
    if not Tracking.objects.filter(id=int(key)).exists():
        return render(request, "apps/tracking_detail.html", {"message":"cannot find the tracking id in our system", "not_found":"true"})
    tracking = Tracking.objects.get(id=int(key))
    tracking.strStatus = getStatus(tracking)
    return render(request, "apps/tracking_detail.html", {"tracking":tracking})

@login_required
def user_info(request):
    trackings = request.user.trackings.all()
    user_packages = []
    for tracking in trackings:
        #do the combination for user_package
        user_package = deepcopy(tracking)
        if tracking.finished:
            user_package.strStatus = "delivered"
            user_package.trunk_id = tracking.trunk_id
        elif not tracking.assigned_trunk:
            user_package.strStatus = "created"
        else:
            user_package.strStatus = intToStatus(Trunk.objects.get(trunk_id=tracking.trunk_id).status)
            user_package.trunk_id = tracking.trunk_id
        user_package.items = []
        for Atran in tracking.amazontransactions.all():
            item = deepcopy(Atran);
            user_package.items.append(item)
        user_packages.append(user_package)
    print(user_packages)
    return render(request, "apps/user_info.html", {"packages":user_packages})

@login_required
def change_destination(request, id):
    tracking = Tracking.objects.get(tracking_id=id)
    if request.method == "POST":
        if "new_destination_x" in request.POST:
            new_destination_x = request.POST["new_destination_x"]
            if not is_valid_number(new_destination_x):
                return redirect("user_info")
            else:
                tracking.to_x = int(new_destination_x)
        if "new_destination_y" in request.POST:
            new_destination_y = request.POST["new_destination_y"]
            if not is_valid_number(new_destination_y):
                return redirect("user_info")
            else:
                tracking.to_y = int(new_destination_y)
        tracking.save()
    return redirect("user_info")

def is_valid_number(value):
    if value == "NaN":
        return False
    try:
        int(value)
        return True
    except ValueError:
        return False

def admin_map(request):
    temp_trunks = Trunk.objects.all()
    trunks = []
    for temp_trunk in temp_trunks:
        trunk = deepcopy(temp_trunk)
        trunk.strStatus = "Trunk id: " + str(trunk.trunk_id) + "  "+ intToStatus(trunk.status)
        trunks.append(trunk)

    temp_warehouses = Warehouse.objects.all()
    warehouses = []
    for temp_warehouse in temp_warehouses:
        warehouse = deepcopy(temp_warehouse)
        warehouse.strStatus = "Warehouse id: " + str(warehouse.warehouse_id)
        warehouses.append(warehouse)
    return render(request, "apps/admin_map.html", {"trunks":trunks, "warehouses":warehouses})

@login_required
def add_prime(request, id):
    tracking = Tracking.objects.get(tracking_id=id)
    if request.method == "POST":
        balance = request.user.balance.all()[0] #get the balance for this user
        if balance.balance >= 20:
            balance.balance -= 20
            balance.save()
            tracking.is_prime = True
            tracking.save()
    return redirect("user_info")

@csrf_exempt
def request_pickup(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    tracking = Tracking()
    if "shipid" in body:
        tracking.tracking_id = body["shipid"]
    if "whid" in body:
        tracking.warehouse_id = body["whid"]
    if "x" in body:
        tracking.to_x = body["x"]
    if "y" in body:
        tracking.to_y = body["y"]
    if ("upsAccount" in body) and (User.objects.filter(username=body["upsAccount"]).exists()):
        tracking.user = User.objects.get(username=body["upsAccount"])
    tracking.save()
    if "products" in body:
        for product_json in body["products"]:
            product = tracking.amazontransactions.create()
            product.product_id = product_json["product_id"]
            product.count = product_json["count"]
            product.items_detail = product_json["description"]
            product.save()
    return JsonResponse({'tracking_id': body["shipid"]})

@csrf_exempt
def initial_trunks(request):
    return 123

def find_best_trunk(x, y):
    trunks = Trunk.objects.filter(status=0).all()
    best_trunk = {}
    for trunk in trunks:
        if not best_trunk:
            best_trunk = trunk
        elif ((abs(trunk.last_x - x) + abs(trunk.last_y - y)) < (abs(best_trunk.last_x - x) + abs(best_trunk.last_y - y))):
            best_trunk = trunk
    return best_trunk

@csrf_exempt
def search_trunk(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    tracking = Tracking.objects.get(tracking_id=body["tracking_id"])
    if Trunk.objects.filter(status=0).exists(): #if some trunks are idle
        trunk = {}
        if Warehouse.objects.filter(warehouse_id=tracking.warehouse_id).exists():
            warehouse = Warehouse.objects.get(warehouse_id=tracking.warehouse_id)
            trunk = find_best_trunk(warehouse.x, warehouse.y)
        else:
            trunk = Trunk.objects.filter(status=0).all()[0]
        trunk.status = 1
        trunk.tracking_id = tracking.tracking_id
        trunk.save()
        tracking.assigned_trunk = True
        tracking.trunk_id = trunk.trunk_id
        tracking.save()
        return JsonResponse({'trunk_id': trunk.trunk_id, "is_prime": tracking.is_prime})
    else:
        return JsonResponse({'trunk_id': -1, "is_prime": tracking.is_prime})

@csrf_exempt
def arrive_warehouse(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    trunk = Trunk.objects.get(trunk_id=body["trunk_id"])
    trunk.status = 2
    trunk.last_x = body["x"]
    trunk.last_y = body["y"]
    trunk.save()
    tracking = Tracking.objects.get(tracking_id=trunk.tracking_id)
    if not Warehouse.objects.filter(warehouse_id=tracking.warehouse_id).exists():
        warehouse = Warehouse.create(tracking.warehouse_id)
        warehouse.x = body["x"]
        warehouse.y = body["y"]
        warehouse.save()
    return JsonResponse({"trunk_id": body["trunk_id"], "tracking_id": tracking.tracking_id ,'warehouse_id': tracking.warehouse_id})

@csrf_exempt
def request_deliver(request):
    #get the x,y and send to deamon
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    return 123

@csrf_exempt
def finish_deliver(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    trunk = Trunk.objects.get(trunk_id=body["trunk_id"])
    trunk.status = 0
    trunk.last_x = body["x"]
    trunk.last_y = body["y"]
    trunk.save()
    tracking = Tracking.objects.get(tracking_id=trunk.tracking_id)
    tracking.finished = True
    tracking.save()
    return JsonResponse({"status": "success"})
