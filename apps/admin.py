from django.contrib import admin

# Register your models here.
from .models import  AmazonAccount, Warehouse, Trunk, AmazonTransaction, Tracking

admin.site.register(AmazonAccount)
admin.site.register(Warehouse)
admin.site.register(Trunk)
admin.site.register(AmazonTransaction)
admin.site.register(Tracking)
