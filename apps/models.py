from django.db import models
from django.contrib.auth.models import User

class Warehouse(models.Model):
    warehouse_id = models.IntegerField()
    x = models.IntegerField(default=0)
    y = models.IntegerField(default=0)

class Trunk(models.Model):
    trunk_id = models.IntegerField()
    last_x = models.IntegerField(default=0) #record the last pos it arrived
    last_y = models.IntegerField(default=0)
    # 0:idle  1:trunk to warehouse  2:trunk waiting in warehouse 3:out for delivery
    status = models.IntegerField(default=0)
    def __str__(self):
        return str(self.trunk_id)

class Tracking(models.Model):
    # tracking id can be created automatically
    tracking_id = models.IntegerField(default=0)
    trunk = models.OneToOneField(Trunk, blank=True, null=True, related_name="tracking")
    to_x = models.IntegerField(blank=True, null=True)
    to_y = models.IntegerField(blank=True, null=True)
    finished = models.BooleanField(default=False)
    assigned_trunk = models.BooleanField(default=False)
    is_prime = models.BooleanField(default=False)
    warehouse_id = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="trackings", null=True)
    def __str__(self):
        return "tracking Id: " + str(self.tracking_id)

class AmazonTransaction(models.Model):
    tracking = models.ForeignKey(Tracking, on_delete=models.CASCADE, related_name="amazontransactions")
    product_id = models.IntegerField(default=0)
    items_detail = models.CharField(default=0, max_length=1000);
    count = models.IntegerField(default=1)
    def __str__(self):
        return "product Id: " + str(self.product_id) + " count: " + str(self.count)
