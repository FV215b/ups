from django.contrib import admin

# Register your models here.
from .models import  Trunk, AmazonTransaction, Tracking, Warehouse, Redeem

admin.site.register(Trunk)
admin.site.register(AmazonTransaction)
admin.site.register(Tracking)
admin.site.register(Warehouse)
admin.site.register(Redeem)
