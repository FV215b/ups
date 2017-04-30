from django.db import models
from django.contrib.auth.models import User

class Warehouse(models.Model):
    warehouse_id = models.IntegerField()
    x = models.IntegerField(default=0)
    y = models.IntegerField(default=0)
    def __str__(self):
        return str(self.warehouse_id)

    @classmethod
    def create(cls, warehouse_id):
        warehouse = cls(warehouse_id=warehouse_id)
        return warehouse

class Redeem(models.Model):
    code = models.CharField(max_length=20)
    amount = models.IntegerField(default=5)

    def __str__(self):
        return (self.code)
    @classmethod
    def create(cls, code):
        redeem = cls(code=code)
        return redeem

class Trunk(models.Model):
    trunk_id = models.IntegerField()
    last_x = models.IntegerField(default=0) #record the last pos it arrived
    last_y = models.IntegerField(default=0)
    tracking_id = models.IntegerField(blank=True, null=True)
    # 0:idle  1:trunk to warehouse  2:trunk waiting in warehouse 3:out for delivery
    status = models.IntegerField(default=0)
    def __str__(self):
        return str(self.trunk_id)

class Tracking(models.Model):
    # tracking id can be created automatically
    tracking_id = models.IntegerField(default=0)
    trunk_id = models.IntegerField(blank=True, null=True)
    to_x = models.IntegerField(blank=True, null=True)
    to_y = models.IntegerField(blank=True, null=True)
    finished = models.BooleanField(default=False)
    assigned_trunk = models.BooleanField(default=False)
    is_prime = models.BooleanField(default=False)
    warehouse_id = models.IntegerField(default=0)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name="trackings")
    def __str__(self):
        return "tracking Id: " + str(self.tracking_id)

class AmazonTransaction(models.Model):
    tracking = models.ForeignKey(Tracking, on_delete=models.CASCADE, related_name="amazontransactions")
    product_id = models.IntegerField(default=0)
    items_detail = models.CharField(default=0, max_length=1000);
    count = models.IntegerField(default=1)
    def __str__(self):
        return "product Id: " + str(self.product_id) + " count: " + str(self.count)
