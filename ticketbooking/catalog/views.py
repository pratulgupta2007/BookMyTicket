from django.views import generic
import random
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.core.mail import send_mail
import json
import uuid
from django.conf import settings

# Create your views here.
from .models import (
    wallet,
    transactions,
    user,
    adminuser,
    foods,
    shows,
    movies,
    tickets,
    OtpToken,
)
from .forms import TicketForm, BillingForm, ConfirmRefund


def index(request):

    movielist = movies.objects.order_by("movie").values_list("movie").distinct()
    ls = random.sample(range(0, len(movielist)), 3)

    context = {
        "show1": movielist[ls[0]][0],
        "show2": movielist[ls[1]][0],
        "show3": movielist[ls[2]][0],
        "num_theaters": adminuser.objects.all().count(),
        "num_foods": foods.objects.count(),
    }
    if request.user.is_authenticated:
        try:
            context["balance"] = user.objects.filter(user=(request.user))[
                0
            ].walletid.balance
        except IndexError:
            n = wallet.objects.create()
            user.objects.create(user=request.user, walletid=n)
            context["balance"] = user.objects.filter(user=(request.user))[
                0
            ].walletid.balance
    return render(request, "index.html", context=context)


class MoviesListView(generic.ListView):
    model = movies
    context_object_name = "movielist"
    template_name = "catalog/movie_list.html"


class MovieDetailView(generic.DetailView):
    model = movies

    def get_context_data(self, **kwargs):
        context = super(MovieDetailView, self).get_context_data(**kwargs)
        showslist = shows.objects.filter(movie_id=context["movies"].movie).filter(
            date_time__gt=timezone.now()
        )
        context["languages"] = (
            showslist.order_by("language").values_list("language", flat=True).distinct()
        )
        context["types"] = (
            showslist.order_by("type").values_list("type", flat=True).distinct()
        )
        context["shows"] = [[x, ""] for x in showslist.order_by("date_time")]
        for x in context["shows"]:
            x[1] = adminuser.objects.filter(theater_name=x[0].get_theatername())[
                0
            ].get_theater_url()
        return context

    template_name = "catalog/movie_detail.html"


class TheaterListView(generic.ListView):
    model = adminuser
    context_object_name = "theaterlist"
    template_name = "catalog/theater_list.html"


class TheaterDetailView(generic.DetailView):
    model = adminuser
    template_name = "catalog/theater_detail.html"

    def get_context_data(self, **kwargs):
        context = super(TheaterDetailView, self).get_context_data(**kwargs)
        showslist = shows.objects.filter(adminID=context["adminuser"].aid).filter(
            date_time__gt=timezone.now()
        )
        context["shows"] = [[x, ""] for x in showslist.order_by("date_time")]
        for x in context["shows"]:
            x[1] = movies.objects.filter(movie=x[0].get_moviename())[
                0
            ].get_absolute_url()
        return context


@login_required
def ShowDetailView(request, pk):
    error = None
    show = shows.objects.get(pk=pk)
    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data["ticket_no"]
            if timezone.now() > show.date_time:
                error = "Show date passed"
            elif data > show.availableseats():
                error = "Seats not available"
            else:
                tempticket = json.dumps(
                    {
                        "count": str(data),
                        "show": str(show.showID),
                        "user": str(request.user),
                        "price": str(show.price),
                    }
                )
                request.session["tempticket"] = tempticket
                return HttpResponseRedirect(reverse("billing"))
    else:
        form = TicketForm()

    context = {"show": show, "form": form, "error": error}
    return render(request, "catalog/show_detail.html", context=context)


@login_required
def ProfileView(request):
    try:
        context = {
            "balance": user.objects.filter(user=(request.user))[0].walletid.balance
        }
    except IndexError:
        n = wallet.objects.create()
        user.objects.create(user=request.user, walletid=n)
        context = {
            "balance": user.objects.filter(user=(request.user))[0].walletid.balance
        }
    return render(request, "account/profile.html", context=context)


@login_required
def AddBalanceView(request):
    return render(request, "account/balance.html")


@login_required
def TicketsView(request):
    ticketlist = tickets.objects.filter(user=(request.user)).filter(verified=True)
    context = {"tickets": ticketlist}
    return render(request, "account/ticketslist.html", context=context)


@login_required
def BillingView(request):
    error = None
    context = {}
    try:
        tempticket = json.loads(request.session["tempticket"])

        if tempticket["user"] == str(request.user):
            temp = {
                "count": int(tempticket["count"]),
                "show": shows.objects.get(pk=uuid.UUID(tempticket["show"])),
                "price": float(tempticket["price"]),
            }
            context = temp
            context["total"] = context["count"] * context["price"]
            if (
                context["total"]
                > user.objects.filter(user=(request.user))[0].walletid.balance
            ):
                error = "Insufficient balance."
            else:
                if request.method == "POST":
                    form = BillingForm(request.POST)
                    if form.is_valid():
                        unverified_tr = transactions.objects.create(
                            sendingID=user.objects.filter(user=(request.user))[
                                0
                            ].walletid,
                            receivingID=temp["show"].adminID.walletid,
                            amount=context["total"],
                            status="I",
                        )
                        unverified_ticket = tickets.objects.create(
                            user=request.user,
                            show=temp["show"],
                            count=temp["count"],
                            total=context["total"],
                            transaction=unverified_tr,
                        )
                        request.session["toverify"] = "ticket%" + str(
                            unverified_ticket.ticketID
                        )
                        request.session["tempticket"] = ""
                        return redirect("verification")
                else:
                    form = BillingForm()
                context["form"] = form
        else:
            "Access denied."
    except KeyError:
        error = "Access denied."
    context["error"] = error
    return render(request, "account/billing.html", context=context)


@login_required
def VerificationView(request):
    User = request.user
    context = {}
    try:
        if request.method == "POST":
            # valid token
            user_otp = OtpToken.objects.filter(user=User).last()
            if user_otp.otp_code == request.POST["otp_code"]:

                if user_otp.otp_expires_at > timezone.now():
                    verifyobj = request.session["toverify"].split("%")
                    if verifyobj[0] == "ticket":
                        t = tickets.objects.get(pk=uuid.UUID(verifyobj[1]))
                        t.verified = True
                        t.save()

                        t.transaction.status = "C"
                        t.transaction.save()

                        userobj = user.objects.filter(user=(t.user))[0]
                        userobj.walletid.balance = userobj.walletid.balance - t.total
                        userobj.walletid.save()
                        t.transaction.receivingID.balance = (
                            t.transaction.receivingID.balance + t.total
                        )
                        t.transaction.receivingID.save()

                        t.show.seats_booked = t.show.seats_booked + t.count
                        t.show.save()

                        user_otp.delete()

                        request.session["toverify"] = ""

                        return redirect("ticketslist")
                else:
                    context["error"] = "The OTP has expired, get a new OTP!"
                    return redirect("verification")

            else:
                context["error"] = "Invalid OTP entered, enter a valid OTP!"
                return redirect("verification")
        elif request.session["toverify"] != "":
            otp = OtpToken.objects.create(
                user=User, otp_expires_at=timezone.now() + timezone.timedelta(minutes=5)
            )

            subject = "Email Verification"
            message = f"""
                                Hi {User.username}, here is your OTP {otp.otp_code} 
                                it expires in 5 minute, use the url below to redirect back to the website
                                http://127.0.0.1:8000/accounts/verification/
                                
                                """
            sender = settings.EMAIL_HOST_USER
            receiver = [
                User.email,
            ]

            send_mail(
                subject,
                message,
                sender,
                receiver,
                fail_silently=False,
            )
    except KeyError:
        context["error"] = "Access denied."

    return render(request, "account/verification.html", context=context)


@login_required
def resend_otp(request):
    if request.method == "POST":
        otp = OtpToken.objects.create(
            user=user, otp_expires_at=timezone.now() + timezone.timedelta(minutes=5)
        )

        subject = "Email Verification"
        message = f"""
                            Hi {request.user.username}, here is your OTP {otp.otp_code} 
                            it expires in 5 minute, use the url below to redirect back to the website
                            http://127.0.0.1:8000/accounts/verification/
                            
                            """
        sender = settings.EMAIL_HOST_USER
        receiver = [
            user.email,
        ]
        user_otp = OtpToken.objects.filter(user=user).last()

        send_mail(
            subject,
            message,
            sender,
            receiver,
            fail_silently=False,
        )
        return redirect("verification")

    return render(request, "account/resend_otp.html")


@login_required
def RefundView(request, ticket):
    context = {}
    if request.method == "POST":
        form = ConfirmRefund(request.POST)
        if form.is_valid():
            ticket = tickets.objects.get(pk=ticket)
            ticket.revertticket()
            return HttpResponseRedirect(reverse("ticketslist"))
    else:
        form = TicketForm()
    return render(request, "account/refund.html")
