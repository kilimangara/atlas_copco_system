# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-06 19:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_auto_20171104_1714'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='address',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Address'),
        ),
    ]
