# Generated by Django 5.1.2 on 2024-11-01 16:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0015_tickets_total'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tickets',
            name='total',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
    ]
