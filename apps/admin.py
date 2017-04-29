from django.contrib import admin

# Register your models here.
from .models import  Trunk, AmazonTransaction, Tracking, Warehouse

admin.site.register(Trunk)
admin.site.register(AmazonTransaction)
admin.site.register(Tracking)
admin.site.register(Warehouse)
