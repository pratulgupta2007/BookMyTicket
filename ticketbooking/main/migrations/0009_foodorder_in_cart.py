# Generated by Django 5.1.2 on 2024-11-23 00:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_remove_foodorder_status_foodorder_verified'),
    ]

    operations = [
        migrations.AddField(
            model_name='foodorder',
            name='in_cart',
            field=models.BooleanField(default=1),
        ),
    ]
