# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-29 19:10
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0025_warehouse'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tracking',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='trackings', to=settings.AUTH_USER_MODEL),
        ),
    ]
