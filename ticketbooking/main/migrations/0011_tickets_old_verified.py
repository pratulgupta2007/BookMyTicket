# Generated by Django 5.1.2 on 2024-11-23 02:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_foodorder_bound_foodorder_old_verified'),
    ]

    operations = [
        migrations.AddField(
            model_name='tickets',
            name='old_verified',
            field=models.BooleanField(default=0),
        ),
    ]
