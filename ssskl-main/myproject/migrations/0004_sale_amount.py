# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-26 18:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myproject', '0003_auto_20151226_1832'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale',
            name='amount',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
