from django.db import models
from django.contrib.auth.models import User

class AmazonAccount(models.Model):
    account = models.CharField(max_length=50);
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="amazonAccount")
    def __str__(self):
        return self.account + ": " + self.user.username
    @classmethod
    def create(cls, user):
        reporter = cls(user=user)
        # do something with the book
        return reporter

class Warehouse(models.Model):
    warehouse_id = models.IntegerField()
    x = models.IntegerField(default=0)
    y = models.IntegerField(default=0)
    def __str__(self):
        return str(self.warehouse_id)

class Trunk(models.Model):
    trunk_id = models.IntegerField()
    last_x = models.IntegerField(default=0, null=True) #record the last pos it arrived
    last_y = models.IntegerField(default=0, null=True)
    # 0:created  1:trunk to warehouse  2:trunk waiting in warehouse 3:out for delivery
    status = models.IntegerField(default=0)
    def __str__(self):
        return str(self.trunk_id)

class AmazonTransaction(models.Model):
    transaction_id = models.IntegerField()
    amazonAccount = models.ForeignKey(AmazonAccount, on_delete=models.CASCADE, related_name="amazonTransactions")
    def __str__(self):
        return "amazon tras Id: " + str(self.transaction_id)

class Tracking(models.Model):
    # tracking id can be created automatically
    trunk = models.ForeignKey(Trunk, blank=True, null=True)
    amazonTransaction = models.OneToOneField(AmazonTransaction, on_delete=models.CASCADE, related_name="tracking")
    to_x = models.IntegerField(blank=True, null=True)
    to_y = models.IntegerField(blank=True, null=True)
    def __str__(self):
        return "trunk travel Id: " + str(self.id)
