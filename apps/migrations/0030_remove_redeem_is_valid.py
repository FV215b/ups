# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-30 17:07
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0029_redeem'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='redeem',
            name='is_valid',
        ),
    ]
