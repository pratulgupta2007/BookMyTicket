# Generated by Django 5.1.2 on 2024-11-01 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0012_remove_wallet_transaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='tickets',
            name='count',
            field=models.IntegerField(default=1),
        ),
    ]