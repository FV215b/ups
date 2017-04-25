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

def home(request):
    trackings = []
    tracking_statuses = []
    for tracking in Tracking.objects.all():
        tracking.strStatus = intToStatus(tracking.trunk.status)
        trackings.append(tracking)
    print(trackings)
    return render(request, "apps/all_list.html", {"trackings":trackings})

def tracking_detail(request, key):
    if not Tracking.objects.filter(id=int(key)).exists():
        return render(request, "apps/tracking_detail.html", {"message":"cannot find the tracking id in our system", "not_found":"true"})
    tracking = Tracking.objects.get(id=int(key))
    tracking.strStatus = intToStatus(tracking.trunk.status)
    return render(request, "apps/tracking_detail.html", {"tracking":tracking})
