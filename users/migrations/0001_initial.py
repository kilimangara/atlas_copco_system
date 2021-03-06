# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-21 00:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=255)),
                ('is_admin', models.BooleanField(default=False)),
                ('slug', models.SlugField()),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=255, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('last_login', models.DateTimeField(blank=True, null=True)),
                ('password', models.CharField(max_length=128)),
                ('is_admin', models.BooleanField(default=False)),
                ('confirmation_token', models.CharField(max_length=48)),
                ('token', models.CharField(max_length=128)),
                ('account', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='staff', to='users.Account')),
            ],
        ),
    ]
