from django.utils import timezone
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
import json
import uuid
import random

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
from .decorators import user_passes_test_with_logout

@user_passes_test_with_logout()
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


@user_passes_test_with_logout()
def AddBalanceView(request):
    return render(request, "account/balance.html")


@user_passes_test_with_logout()
def TicketsView(request):
    ticketlist = tickets.objects.filter(user=(request.user)).filter(verified=True)
    context = {"tickets": ticketlist}
    return render(request, "account/ticketslist.html", context=context)


@user_passes_test_with_logout()
def BillingView(request):
    error = None
    context = {}
    try:
        tempticket = tickets.objects.get(pk=uuid.UUID(request.session["tempticket"]))

        if tempticket.user == request.user:
            context = {
                "count": tempticket.count,
                "show": tempticket.show,
                "price": tempticket.total/tempticket.count,
                "total": tempticket.total,
            }
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
                            sendingID=user.objects.filter(user=(request.user))[0].walletid,
                            receivingID=tempticket.show.adminID.walletid,
                            amount=context["total"],
                            status="I",
                        )
                        tempticket.transaction = unverified_tr
                        tempticket.save()
                        request.session["toverify"] = "ticket%" + str(
                            tempticket.ticketID
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

def OtpEmail(User, otp):
    subject = "Email Verification"
    message = f"""
                Hi {User.username}, here is your OTP {otp}
                """
    sender = settings.EMAIL_HOST_USER
    receiver = [User.email,]
    send_mail(
        subject,
        message,
        sender,
        receiver,
        fail_silently=False,
    )

@user_passes_test_with_logout()
def VerificationView(request):
    User = request.user
    context = {}
    try:
        if request.method == "POST":
            user_otp = OtpToken.objects.filter(user=User).last()

            if user_otp.otp_code == request.POST["otp_code"]:
                if user_otp.otp_expires_at > timezone.now():
                    verifyobj = request.session["toverify"].split("%")

                    if verifyobj[0] == "ticket":
                        t = tickets.objects.get(pk=uuid.UUID(verifyobj[1]))
                        if timezone.now() >= t.show.date_time:
                            error = "Show date passed"
                            return render(request, "account/404.html", context={'error': error})
                        
                        elif t.count > t.show.availableseats():
                            error = "Seats not available"
                            return render(request, "account/404.html", context={'error': error})
                        
                        else:
                            t.verified = True
                            t.save()
                            user_otp.delete()
                            request.session["toverify"] = ""
                            return redirect("ticketslist")

                    elif verifyobj[0] == "food":
                        t = tickets.objects.get(pk=uuid.UUID(verifyobj[1]))
                        if timezone.now() >= t.show.date_time:
                            error = "Show date passed"
                            return HttpResponseRedirect(
                                reverse("food", args=(error,))
                            )
                        
                        else:
                            orders = foodorder.objects.filter(ticket=t).filter(verified=False).filter(in_cart=True)
                            userobj = user.objects.filter(user=(t.user))[0]
                            adminobj = t.show.adminID

                            for order in orders:
                                order.transaction = transactions.objects.create(
                                    sendingID=userobj.walletid,
                                    receivingID=adminobj.walletid,
                                    amount=order.total(),
                                )
                                order.save()
                                order.verified = True
                                order.save()

                            user_otp.delete()
                            request.session["toverify"] = ""
                            return HttpResponseRedirect(reverse("food", args=(str(t.ticketID),)))
                else:
                    context["error"] = "The OTP has expired, get a new OTP!"
                    return redirect("verification")

            else:
                context["error"] = "Invalid OTP entered, enter a valid OTP!"
                return redirect("verification")
            
        elif request.session["toverify"] != "":
            otp = OtpToken.objects.create(
                user=User, otp_expires_at=timezone.now() + timezone.timedelta(minutes=5),
                otp_code=str(random.randint(100000, 999999))
            )
            OtpEmail(request.user, otp.otp_code)

            
    except KeyError:
        context["error"] = "Access denied."

    return render(request, "account/verification.html", context=context)

def ErrorView(request, exception):
    return render(request, 'account/404.html', context={'error': exception})


@user_passes_test_with_logout()
def resend_otp(request):
    if request.method == "POST":
        otp = OtpToken.objects.create(
            user=user, otp_expires_at=timezone.now() + timezone.timedelta(minutes=5),
            otp_code=str(random.randint(100000, 999999))
        )

        OtpEmail(request.user, otp.otp_code)
        return redirect("verification")

    return render(request, "account/resend_otp.html")


@user_passes_test_with_logout()
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


@user_passes_test_with_logout()
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
    context["orders"] = foodorder.objects.filter(ticket=ticket).filter(verified=True)
    context["cart"] = foodorder.objects.filter(ticket=ticket).filter(in_cart=True)
    context["foods"] = foods.objects.filter(adminID=ticket.show.adminID)
    context["ticket"] = ticket
    return render(request, "account/food.html", context=context)


def GenOrder(request, ticket, item):
    ticket = tickets.objects.get(pk=ticket)
    item = foods.objects.get(pk=item)
    try:
        order = foodorder.objects.get_or_create(ticket=ticket, food=item, in_cart=True)
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

@user_passes_test_with_logout()
def RefundFood(request, ticket, order):
    if request.user==foodorder.objects.get(pk=order).ticket.user:
        if request.method == "POST":
            form = ConfirmRefund(request.POST)
            if form.is_valid():
                order = foodorder.objects.get(pk=order)
                order.verified = False
                order.save()
                return HttpResponseRedirect(reverse("food", args=(str(order.ticket.ticketID),)))
        else:
            form = ConfirmRefund()
        return render(request, "account/refundfood.html")
    else:
        return render(request, "account/404.html", context={'error': 'Access Denied'})

    

@user_passes_test_with_logout()
def TransactionsView(request):
    context={
        'transactions':transactions.objects.filter(sendingID=user.objects.get(user=request.user).walletid).exclude(status="I").order_by('-date')
        }
    return render(request, "account/transactions.html", context=context)
