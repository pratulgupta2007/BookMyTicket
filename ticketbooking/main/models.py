from typing import Any
from django.db import models
from django.urls import reverse
import uuid
from django.conf import settings
from django.utils import timezone
import datetime
import pytz

class wallet(models.Model):
    walletid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        if user.objects.filter(walletid=self.walletid).exists():
            return str(user.objects.get(walletid=self.walletid).user.email)
        elif adminuser.objects.filter(walletid=self.walletid).exists():
            return str(adminuser.objects.get(walletid=self.walletid).theater_name)


class transactions(models.Model):
    transactionsID = models.UUIDField(default=uuid.uuid4, primary_key=True)
    sendingID = models.ForeignKey(
        wallet, on_delete=models.CASCADE, related_name="sender"
    )
    receivingID = models.ForeignKey(
        wallet, on_delete=models.CASCADE, related_name="receiver"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=1,
        choices={"I": "Incomplete", "R": "Reverted", "C": "Completed"},
        default="I",
    )
    old_status = None
    date=models.DateTimeField(auto_now_add=True)

    def __init__(self, *args: Any, **kwargs: Any) :
        super().__init__(*args, **kwargs)
        self.old_status = self.status

    def _loaded_values(self):
        return transactions.objects.get(pk=self.pk)

    def __str__(self):
        return str(self.sendingID) + " | " + str(self.receivingID) + " | " + str(self.amount) + " | " + str(self.date)+ " | " + str(self.status)
    
    def save(self, *args, **kwargs):
        if self.status == "C" and (self.old_status == "I" or self.old_status == "R"):
            self.sendingID.balance -= self.amount
            self.sendingID.save()

            self.receivingID.balance += self.amount
            self.receivingID.save()
        elif self.status == "R" and self.old_status == "C":
            self.sendingID.balance += self.amount
            self.sendingID.save()

            self.receivingID.balance -= self.amount
            self.receivingID.save()

        super().save(*args, **kwargs)
        self.old_status = self.status


class user(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    walletid = models.OneToOneField(wallet, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)


class adminuser(models.Model):
    aid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True
    )
    walletid = models.OneToOneField(wallet, on_delete=models.CASCADE)

    theater_name = models.CharField(
        max_length=200, unique=True, help_text="Enter theater name and address: "
    )
    theater_phone = models.CharField(max_length=13)
    theater_email = models.EmailField()
    revenue = models.DecimalField(max_digits=20, decimal_places=2)

    class Meta:
        permissions = (("theateradmin", "User is theater admin"),)

    def __str__(self):
        return self.theater_name

    def get_theater_url(self):
        return reverse("theater-detail", args=[str(self.aid)])


class movies(models.Model):
    slug = models.SlugField(default=uuid.uuid4, unique=True)
    movie = models.CharField(max_length=255, primary_key=True)
    rating = models.CharField(max_length=5, default="UA")
    genre = models.CharField(max_length=20)

    duration = models.DurationField()

    def _str_(self):
        return str(self.movie)

    def get_absolute_url(self):
        return reverse("movie-detail", args=[str(self.slug)])

    def get_duration(self):
        hours, remainder = divmod(self.duration.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        return "%shr %smin" % (int(hours), int(minutes))


class shows(models.Model):
    showID = models.UUIDField(default=uuid.uuid4, primary_key=True)
    adminID = models.ForeignKey(
        adminuser, on_delete=models.CASCADE, related_name="shows"
    )
    movie = models.ForeignKey(movies, on_delete=models.CASCADE, related_name="movies")
    date_time = models.DateTimeField()
    seats = models.IntegerField(default=0)
    seats_booked = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    type = models.CharField(max_length=20, help_text="Enter movie viewing type: ")
    language = models.CharField(max_length=20, help_text="Enter movie language: ")

    def __str__(self):
        return (
            str(self.adminID)
            + " | "
            + self.movie.movie
            + " "
            + self.type
            + " | "
            + str(self.date_time.time())
            + " "
            + str(self.date_time.date())
        )

    def get_absolute_datetime(self):
        nowtz = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
        seconds = nowtz.utcoffset().total_seconds()
        x = datetime.timedelta(seconds=seconds)
        return self.date_time + x

    def get_absolute_url(self):
        return reverse("show-detail", args=[str(self.showID)])

    def get_date(self):
        return self.get_absolute_datetime().date()

    def get_date_str(self):
        return self.get_date().strftime("%Y-%m-%d")

    def get_time(self):
        return self.get_absolute_datetime().time()

    def get_time_str(self):
        return self.get_time().strftime("%H:%M")

    def availableseats(self):
        return self.seats - self.seats_booked


class foods(models.Model):
    foodID = models.UUIDField(default=uuid.uuid4, primary_key=True)
    adminID = models.ForeignKey(adminuser, on_delete=models.CASCADE)
    itemname = models.CharField(max_length=255, unique=True, help_text="Enter item name: ")
    price = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Enter item price: "
    )

    def __str__(self):
        return self.itemname + " | " + self.adminID.theater_name

    def get_absolute_url(self):
        return reverse("show", args=[str(self.foodID)])


class tickets(models.Model):
    ticketID = models.UUIDField(default=uuid.uuid4, primary_key=True)
    count = models.IntegerField(default=1)
    total = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    show = models.ForeignKey(shows, on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True
    )
    transaction = models.OneToOneField(transactions, on_delete=models.CASCADE, null=True)
    verified = models.BooleanField(default=0)
    old_verified = models.BooleanField(default=0)

    def __init__(self, *args: Any, **kwargs: Any) :
        super().__init__(*args, **kwargs)
        self.old_verified = self.verified
    
    def __str__(self):
        return str(self.user) + " | " + str(self.show) + " | " + str(self.count)

    def _loaded_values(self):
        return transactions.objects.get(pk=self.pk)

    def revertticket(self):
        if self.show.date_time > timezone.now():
            self.transaction.status = "R"
            self.transaction.save()
            self.verified = False
            self.save()
            return True
        else:
            return False
    
    def save(self, *args, **kwargs):
        if self.verified == True and self.old_verified == False:
            if self.show.date_time < timezone.now():
                raise ValueError("Show date has passed.")
            else:
                self.transaction.status = "C"
                self.transaction.save()
                self.show.seats_booked += self.count
                self.show.save()
                for order in foodorder.objects.filter(ticket=self).filter(in_cart=False):
                    if order.bound==True:
                        order.verified = True
                        order.save()

        elif self.verified == False and self.old_verified == True:
            self.show.seats_booked -= self.count
            for order in foodorder.objects.filter(ticket=self, in_cart=False, verified=True):
                #self.total -= order.total()
                order.verified = False
                order.bound=True
                order.save()
            self.show.save()
        super().save(*args, **kwargs)
        self.old_verified = self.verified


class OtpToken(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="otps"
    )
    otp_code = models.CharField(max_length=6, default=' ')
    otp_created_at = models.DateTimeField(auto_now_add=True)
    otp_expires_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.user.email

    

class foodorder(models.Model):
    
    orderID = models.UUIDField(default=uuid.uuid4, primary_key=True)
    ticket = models.ForeignKey(tickets, on_delete=models.CASCADE)
    food = models.ForeignKey(foods, on_delete=models.CASCADE)
    count = models.IntegerField(default=1)
    transaction = models.ForeignKey(transactions, on_delete=models.CASCADE, null=True)
    verified = models.BooleanField(default=0)
    in_cart = models.BooleanField(default=1)
    bound=models.BooleanField(default=0)
    old_verified = models.BooleanField(default=0)

    def __init__(self, *args: Any, **kwargs: Any) :
        super().__init__(*args, **kwargs)
        self.old_verified = self.verified
        
    def __str__(self):
        return str(self.ticket) + " | " + str(self.food) + " | " + str(self.count)

    def total(self):
        return self.count * self.food.price
    
    def save(self, *args, **kwargs):
        if self.verified == True and self.old_verified == False:
            if self.ticket.show.date_time < timezone.now():
                raise ValueError("Show date has passed.")
            else:
                self.in_cart = False
                self.transaction.status = "C"
                self.ticket.total += self.total()
                self.ticket.save()
                self.transaction.save()
                self.bound=False
        elif self.verified == False and self.old_verified == True:
            if self.ticket.show.date_time < timezone.now():
                raise ValueError("Show date has passed.")
            else:
                self.transaction.status = "R"
                self.ticket.total -= self.total()
                self.ticket.save()
                self.transaction.save()
        super().save(*args, **kwargs)
        self.old_verified = self.verified
        
