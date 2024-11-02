from django.db import models
from django.urls import reverse
import uuid
from django.http import HttpRequest
from django.conf import settings

from django.contrib.auth import get_user_model
User = get_user_model()

class wallet(models.Model):
    walletid=models.UUIDField(default=uuid.uuid4, primary_key=True)
    balance=models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return str(self.walletid)

class transactions(models.Model):
    transactionsID=models.UUIDField(default=uuid.uuid4, primary_key=True)
    sendingID=models.ForeignKey(wallet, on_delete=models.CASCADE, related_name="sender")
    receivingID=models.ForeignKey(wallet, on_delete=models.CASCADE, related_name="receiver")
    amount=models.DecimalField(max_digits=10, decimal_places=2)
    status=models.CharField(max_length=1,
                            choices={
                                "I": "Incomplete",
                                "R": "Reverted",
                                "C": "Completed"
                            }, default="I")


class user(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    walletid=models.ForeignKey(wallet, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)


class adminuser(models.Model):
    aid=models.UUIDField(default=uuid.uuid4, primary_key=True)
    password=models.CharField(max_length=200)
    verification_email=models.EmailField()
    walletid=models.ForeignKey(wallet, on_delete=models.CASCADE)

    #Theater related information
    theater_name=models.CharField(max_length=200, unique=True, help_text="Enter theater name and address: ")
    theater_phone=models.CharField(max_length=13)
    theater_email=models.EmailField()
    revenue=models.DecimalField(max_digits=20, decimal_places=2)

    def __str__(self):
        return self.theater_name
    
    def get_theater_url(self):
        return reverse('theater-detail', args=[str(self.aid)])
    
    def get_absolute_url(self):
        return reverse('admin-info', args=[str(self.aid)])

class movies(models.Model):
    slug=models.SlugField(default=uuid.uuid4, unique=True)
    movie=models.CharField(max_length=255, primary_key=True)
    rating=models.CharField(max_length=5, default='UA')
    genre=models.CharField(max_length=20)
    
    duration=models.DurationField()

    def _str_(self):
        return str(self.movie)
    
    def get_absolute_url(self):
        return reverse('movie-detail', args=[str(self.slug)])
    
    def get_duration(self):
        hours, remainder = divmod(self.duration.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        return '%shr %smin' %(int(hours), int(minutes))


class shows(models.Model):
    showID=models.UUIDField(default=uuid.uuid4, primary_key=True)
    adminID=models.ForeignKey(adminuser, on_delete=models.CASCADE, related_name='shows')
    movie=models.ForeignKey(movies, on_delete=models.CASCADE, related_name='movies')
    date_time=models.DateTimeField()
    seats=models.IntegerField(default=0)
    seats_booked=models.IntegerField(default=0)
    price=models.DecimalField(max_digits=10, decimal_places= 2, default=0.0)
    type=models.CharField(max_length=20, help_text="Enter movie viewing type: ")
    language=models.CharField(max_length=20, help_text="Enter movie language: ")

    def __str__(self):
        return str(self.adminID)+' | '+self.movie.movie + ' ' + self.type+ ' | ' + str(self.date_time.time()) + ' ' + str(self.date_time.date())

    def get_absolute_url(self):
        return reverse('show-detail', args=[str(self.showID)])
    
    def get_moviename(self):
        return self.movie.movie
    
    def get_theatername(self):
        return self.adminID
    
    def get_date(self):
        return self.date_time.date()
    
    def get_time(self):
        return self.date_time.time()
    
    def availableseats(self):
        return self.seats-self.seats_booked

class foods(models.Model):
    foodID=models.UUIDField(default=uuid.uuid4, primary_key=True)
    adminID=models.ForeignKey(adminuser, on_delete=models.CASCADE)
    itemname=models.CharField(max_length=255, help_text="Enter item name: ", unique=True)
    price=models.DecimalField(max_digits=5, decimal_places=2, help_text="Enter item price: ")
    availibilty=models.BooleanField()

    def __str__(self):
        return self.itemname

    def get_absolute_url(self):
        return reverse('show', args=[str(self.foodID)])

class tickets(models.Model):
    ticketID=models.UUIDField(default=uuid.uuid4, primary_key=True)
    count=models.IntegerField(default=1)
    total=models.DecimalField(max_digits=8, decimal_places=2, default=0)
    show=models.ForeignKey(shows, on_delete=models.CASCADE)
    user=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)