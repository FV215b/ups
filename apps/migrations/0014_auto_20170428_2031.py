# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-28 20:31
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0013_auto_20170427_2018'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='amazonaccount',
            name='user',
        ),
        migrations.DeleteModel(
            name='Warehouse',
        ),
        migrations.RemoveField(
            model_name='amazontransaction',
            name='amazonAccount',
        ),
        migrations.DeleteModel(
            name='AmazonAccount',
        ),
    ]
