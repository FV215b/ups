from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models

class AmountBalance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="balance")
    balance = models.IntegerField(default=100)

# Create your models here.
