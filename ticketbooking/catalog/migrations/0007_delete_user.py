# Generated by Django 5.1.2 on 2024-10-27 14:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0006_shows_seats_booked_alter_foods_itemname'),
    ]

    operations = [
        migrations.DeleteModel(
            name='user',
        ),
    ]