# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-31 07:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='address',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='users.Address'),
        ),
    ]
