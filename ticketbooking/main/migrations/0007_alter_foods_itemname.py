# Generated by Django 5.1.2 on 2024-11-22 22:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_transactions_date_alter_adminuser_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='foods',
            name='itemname',
            field=models.CharField(help_text='Enter item name: ', max_length=255, unique=True),
        ),
    ]