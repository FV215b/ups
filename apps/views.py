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

def show_all_list(request):
    tracking_ids = []
    tracking_status = []
    for tracking in Tracking.all():
        tracking_ids.append(tracking.id)
        tracking_status.append(intToStatus(tracking.trunk.status))
    
