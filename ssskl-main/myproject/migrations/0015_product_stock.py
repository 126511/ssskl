# Generated by Django 3.2.8 on 2021-11-15 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myproject', '0014_auto_20211021_2144'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='stock',
            field=models.IntegerField(default=0),
        ),
    ]
