from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseRedirect
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from datetime import datetime
import pytz


# Create your views here.
from .models import (
    adminuser,
    foods,
    shows,
    movies,
    tickets,
)
from .forms import ConfirmRefund, EditShow, EditFood


def is_on_group_check(*groups):
    def on_group_check(user):
        if user.groups is None:
            return False
        return user.groups.filter(name__in=groups).exists()

    return on_group_check


on_admin_group = is_on_group_check("Theater Admin")


def adminlogin(request):
    if request.method == "POST":
        username = request.POST.get("username").lower()
        password = request.POST.get("password")

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "User Not Found")
            return redirect("home")

        if user.groups.filter(name="Theater Admin").exists():
            if user is not None:
                login(
                    request, user, backend="django.contrib.auth.backends.ModelBackend"
                )
                return redirect("panel")
            else:
                messages.error(request, "Username or Password does not match.")
        else:
            messages.error(request, "Access Denied")

    return render(request, "panel/login.html")


@user_passes_test(on_admin_group, login_url="admin_login")
def adminlogout(request):
    logout(request)
    return HttpResponseRedirect(reverse("panel"))


@user_passes_test(on_admin_group, login_url="admin_login")
def panel(request):
    context = {"theater": adminuser.objects.filter(user=request.user)[0]}
    return render(request, "panel/panel.html", context=context)


@user_passes_test(on_admin_group, login_url="admin_login")
def adminfoods(request):
    foodlist = foods.objects.filter(
        adminID=adminuser.objects.filter(user=request.user)[0]
    )
    context = {"foods": foodlist}
    return render(request, "panel/foods.html", context=context)


@user_passes_test(on_admin_group, login_url="admin_login")
def editfood(request, foodID):
    food = foods.objects.get(pk=foodID)
    if request.method == "POST":
        form = EditFood(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            food.itemname = data["itemname"]
            food.price = data["price"]
            food.save()
            return HttpResponseRedirect(reverse("admin_foods"))

    else:
        form = EditFood()
    context = {"food": food, "form": form}
    return render(request, "panel/editfood.html", context=context)


@user_passes_test(on_admin_group, login_url="admin_login")
def newfood(request):
    if request.method == "POST":
        form = EditFood(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            foods.objects.create(
                itemname=data["itemname"],
                price=data["price"],
                adminID=adminuser.objects.filter(user=request.user)[0],
            )
            return HttpResponseRedirect(reverse("admin_foods"))

    else:
        form = EditFood()
    context = {"form": form}
    return render(request, "panel/newfood.html", context=context)


@user_passes_test(on_admin_group, login_url="admin_login")
def refundfood(request, foodID):
    food = foods.objects.get(pk=foodID)
    if request.method == "POST":
        form = ConfirmRefund(request.POST)
        if form.is_valid():
            food.delete()
            return HttpResponseRedirect(reverse("admin_foods"))
    else:
        form = ConfirmRefund()
    return render(request, "panel/refundfood.html")


@user_passes_test(on_admin_group, login_url="admin_login")
def adminshows(request):
    showlist = shows.objects.filter(
        adminID=adminuser.objects.filter(user=request.user)[0]
    )
    context = {"shows": showlist}
    return render(request, "panel/shows.html", context=context)


@user_passes_test(on_admin_group, login_url="admin_login")
def editshow(request, showID):
    show = shows.objects.get(pk=showID)
    movielist = movies.objects.all()
    context = {"show": show, "movies": movielist}
    if show.date_time > timezone.now():
        if request.method == "POST":
            form = EditShow(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                date_time = datetime.strptime(
                    data["date"] + " " + data["time"], "%Y-%m-%d %H:%M"
                )
                date_time = pytz.timezone("Asia/Kolkata").localize(date_time)
                if date_time > timezone.now():
                    price = data["price"]
                    seats = data["seats"]
                    movie = movies.objects.filter(movie=data["movie"])[0]
                    type = data["type"]
                    language = data["language"]

                    show.date_time = date_time
                    show.price = price
                    show.seats = seats
                    show.movie = movie
                    show.type = type
                    show.language = language
                    show.save()
                    return HttpResponseRedirect(reverse("admin_shows"))
                else:
                    form.add_error("date", "Invalid date.")

        else:
            form = EditShow()
    else:
        messages.error(request, "Show date has passed.")
    context = {"show": show, "movies": movielist, "form": form}
    return render(request, "panel/editshow.html", context=context)


@user_passes_test(on_admin_group, login_url="admin_login")
def newshow(request):
    movielist = movies.objects.all()
    context = {"movies": movielist}
    if request.method == "POST":
        form = EditShow(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            date_time = datetime.strptime(
                data["date"] + " " + data["time"], "%Y-%m-%d %H:%M"
            )
            date_time = pytz.timezone("Asia/Kolkata").localize(date_time)
            if date_time > timezone.now():
                price = data["price"]
                seats = data["seats"]
                movie = movies.objects.filter(movie=data["movie"])[0]
                type = data["type"]
                language = data["language"]

                shows.objects.create(
                    date_time=date_time,
                    price=price,
                    seats=seats,
                    movie=movie,
                    type=type,
                    language=language,
                    adminID=adminuser.objects.filter(user=request.user)[0],
                )
                return HttpResponseRedirect(reverse("admin_shows"))
            else:
                form.add_error("date", "Invalid date.")

    else:
        form = EditShow()

    context = {"movies": movielist, "form": form}
    return render(request, "panel/newshow.html", context=context)


@user_passes_test(on_admin_group, login_url="admin_login")
def refundshow(request, showID):
    show = shows.objects.get(pk=showID)
    if show.date_time > timezone.now():
        if request.method == "POST":
            form = ConfirmRefund(request.POST)
            if form.is_valid():
                ticket = tickets.objects.filter(show=show)
                for x in ticket:
                    x.revertticket()
                show.delete()
                return HttpResponseRedirect(reverse("admin_shows"))
        else:
            form = ConfirmRefund()
    else:
        messages.error(request, "Show date has passed.")
    return render(request, "panel/refund.html")
