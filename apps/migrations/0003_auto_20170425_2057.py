# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-25 20:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0002_amazontransaction_items_detail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tracking',
            name='trunk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tracking', to='apps.Trunk'),
        ),
    ]
