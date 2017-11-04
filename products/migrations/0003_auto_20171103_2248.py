# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-03 22:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_auto_20171031_0716'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='quantity',
        ),
        migrations.AddField(
            model_name='invoice',
            name='on_creation',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='product',
            name='responsible_text',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='type_filter',
            field=models.CharField(default='', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='year',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='responsible',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='products', to='users.Account'),
        ),
        migrations.AlterField(
            model_name='product',
            name='sku',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]