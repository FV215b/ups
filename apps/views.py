from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import AmazonAccount
from .models import Warehouse
from .models import Trunk
from .models import AmazonTransaction
from .models import Tracking
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core import serializers
from copy import deepcopy
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
        return intToStatus(tracking.trunk.status)

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
    accounts = request.user.amazonaccount.all()
    if len(accounts) == 0:
        return render(request, "apps/user_info.html", {"not_found":"true"})
    AmazonTransactions = []
    for account in accounts:
        AmazonTransactions = account.amazontransactions.all()
    user_packages = []
    for Atran in AmazonTransactions:
        #do the combination for user_package
        user_package = deepcopy(Atran);
        tracking = Atran.tracking
        user_package.trackingId = tracking.id
        user_package.to_x = tracking.to_x
        user_package.to_y = tracking.to_y
        if tracking.finished:
            user_package.strStatus = "delivered"
            user_package.trunk_id = tracking.trunk.trunk_id
        elif not tracking.assigned_trunk:
            user_package.strStatus = "created"
        else:
            user_package.strStatus = intToStatus(tracking.trunk.status)
            user_package.trunk_id = tracking.trunk.trunk_id
        user_packages.append(user_package)
    print(user_packages)
    return render(request, "apps/user_info.html", {"packages":user_packages})

@login_required
def change_destination(request, id):
    tracking = Tracking.objects.get(id=id)
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
        return int(value) >= 0
    except ValueError:
        return False

def admin_map(request):
    return render(request, "apps/admin_map.html") 
