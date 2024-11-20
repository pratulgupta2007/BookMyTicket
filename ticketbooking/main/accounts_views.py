from django.views import generic
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
import json
import uuid


# Create your views here.
from .models import (
    wallet,
    transactions,
    user,
    foods,
    shows,
    tickets,
    OtpToken,
    foodorder,
)
from .forms import BillingForm, ConfirmRefund


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

                    elif verifyobj[0] == "food":
                        t = tickets.objects.get(pk=uuid.UUID(verifyobj[1]))
                        orders = foodorder.objects.filter(ticket=t).filter(status="I")
                        total = 0
                        userobj = user.objects.filter(user=(t.user))[0]
                        adminobj = t.show.adminID

                        for order in orders:
                            order.status = "C"
                            total += order.total()
                            order.transaction = transactions.objects.create(
                                sendingID=userobj.walletid,
                                receivingID=adminobj.walletid,
                                amount=order.total(),
                                status="C",
                            )
                            order.save()

                        t.total += total
                        t.save()

                        userobj.walletid.balance = userobj.walletid.balance - total
                        userobj.walletid.save()
                        adminobj.walletid.balance = adminobj.walletid.balance + total
                        adminobj.walletid.save()

                        user_otp.delete()
                        request.session["toverify"] = ""
                        return HttpResponseRedirect(
                            reverse("food", args=(str(t.ticketID),))
                        )
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
    if request.method == "POST":
        form = ConfirmRefund(request.POST)
        if form.is_valid():
            ticket = tickets.objects.get(pk=ticket)
            ticket.revertticket()
            return HttpResponseRedirect(reverse("ticketslist"))
    else:
        form = ConfirmRefund()
    return render(request, "account/refund.html")


@login_required
def FoodView(request, ticket):
    ticket = tickets.objects.get(pk=ticket)
    context = {}
    if request.method == "POST":
        form = BillingForm(request.POST)
        if form.is_valid():
            if ticket.show.date_time > timezone.now():
                request.session["toverify"] = "food%" + str(ticket.ticketID)
                return redirect("verification")
    else:
        form = BillingForm()
    context["form"] = form
    context["orders"] = foodorder.objects.filter(ticket=ticket).filter(status="C")
    context["cart"] = foodorder.objects.filter(ticket=ticket).filter(status="I")
    context["foods"] = foods.objects.filter(adminID=ticket.show.adminID)
    context["ticket"] = ticket
    return render(request, "account/food.html", context=context)


def GenOrder(request, ticket, item):
    ticket = tickets.objects.get(pk=ticket)
    item = foods.objects.get(pk=item)
    try:
        order = foodorder.objects.create(ticket=ticket, food=item)
        return HttpResponseRedirect(reverse("food", args=(str(ticket.ticketID),)))
    except Exception as e:
        print(e)
        pass
    return render(request, "account/genorder.html")


def AddReduceOrder(request, ticket, order, operation):
    ticket = tickets.objects.get(pk=ticket)
    order = foodorder.objects.get(pk=order)
    try:
        if operation == "add":
            order.count += 1
            order.save()
            return HttpResponseRedirect(reverse("food", args=(str(ticket.ticketID),)))
        elif operation == "reduce":
            if order.count == 1:
                order.delete()
                return HttpResponseRedirect(
                    reverse("food", args=(str(ticket.ticketID),))
                )
            else:
                order.count -= 1
                order.save()
                return HttpResponseRedirect(
                    reverse("food", args=(str(ticket.ticketID),))
                )
        elif operation == "delete":
            order.delete()
            return HttpResponseRedirect(reverse("food", args=(str(ticket.ticketID),)))
    except:
        pass
    return render(request, "account/genorder.html")


@login_required
def TransactionsView(request):
    return render(request, "account/transactions.html")
