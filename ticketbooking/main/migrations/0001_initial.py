# Generated by Django 5.1.2 on 2024-11-07 21:38

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='adminuser',
            fields=[
                ('aid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('password', models.CharField(max_length=200)),
                ('verification_email', models.EmailField(max_length=254)),
                ('theater_name', models.CharField(help_text='Enter theater name and address: ', max_length=200, unique=True)),
                ('theater_phone', models.CharField(max_length=13)),
                ('theater_email', models.EmailField(max_length=254)),
                ('revenue', models.DecimalField(decimal_places=2, max_digits=20)),
            ],
        ),
        migrations.CreateModel(
            name='movies',
            fields=[
                ('slug', models.SlugField(default=uuid.uuid4, unique=True)),
                ('movie', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('rating', models.CharField(default='UA', max_length=5)),
                ('genre', models.CharField(max_length=20)),
                ('duration', models.DurationField()),
            ],
        ),
        migrations.CreateModel(
            name='transactions',
            fields=[
                ('transactionsID', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('I', 'Incomplete'), ('R', 'Reverted'), ('C', 'Completed')], default='I', max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='wallet',
            fields=[
                ('walletid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('balance', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='foods',
            fields=[
                ('foodID', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('itemname', models.CharField(help_text='Enter item name: ', max_length=255, unique=True)),
                ('price', models.DecimalField(decimal_places=2, help_text='Enter item price: ', max_digits=5)),
                ('availibilty', models.BooleanField()),
                ('adminID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.adminuser')),
            ],
        ),
        migrations.CreateModel(
            name='OtpToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('otp_code', models.CharField(default='6564bb', max_length=6)),
                ('tp_created_at', models.DateTimeField(auto_now_add=True)),
                ('otp_expires_at', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='otps', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='shows',
            fields=[
                ('showID', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('date_time', models.DateTimeField()),
                ('seats', models.IntegerField(default=0)),
                ('seats_booked', models.IntegerField(default=0)),
                ('price', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('type', models.CharField(help_text='Enter movie viewing type: ', max_length=20)),
                ('language', models.CharField(help_text='Enter movie language: ', max_length=20)),
                ('adminID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shows', to='main.adminuser')),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='movies', to='main.movies')),
            ],
        ),
        migrations.CreateModel(
            name='tickets',
            fields=[
                ('ticketID', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('count', models.IntegerField(default=1)),
                ('total', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('verified', models.BooleanField(default=0)),
                ('show', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.shows')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('transaction', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.transactions')),
            ],
        ),
        migrations.CreateModel(
            name='foodorder',
            fields=[
                ('orderID', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('count', models.IntegerField(default=1)),
                ('status', models.CharField(choices=[('I', 'Incomplete'), ('C', 'Completed')], default='I', max_length=1)),
                ('food', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.foods')),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.tickets')),
                ('transaction', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.transactions')),
            ],
        ),
        migrations.CreateModel(
            name='user',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('walletid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.wallet')),
            ],
        ),
        migrations.AddField(
            model_name='transactions',
            name='receivingID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receiver', to='main.wallet'),
        ),
        migrations.AddField(
            model_name='transactions',
            name='sendingID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sender', to='main.wallet'),
        ),
        migrations.AddField(
            model_name='adminuser',
            name='walletid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.wallet'),
        ),
    ]
