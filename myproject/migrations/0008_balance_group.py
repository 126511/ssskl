# Generated by Django 3.2.8 on 2021-11-25 15:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myproject', '0007_prepaid_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='balance',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='myproject.group'),
        ),
    ]