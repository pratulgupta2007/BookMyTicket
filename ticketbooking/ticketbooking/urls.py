"""
URL configuration for ticketbooking project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
import os

urlpatterns = [
    path("admin/", admin.site.urls),]

if bool(settings.DEBUG):
    from main.panel_views import (
        panel,
        adminlogin,
        adminlogout,
        adminfoods,
        editfood,
        newfood,
        refundfood,
        adminshows,
        editshow,
        newshow,
        refundshow,
    )
    from main.accounts_views import (
        ProfileView,
        AddBalanceView,
        TicketsView,
        BillingView,
        VerificationView,
        resend_otp,
        RefundView,
        FoodView,
        GenOrder,
        AddReduceOrder,
        TransactionsView,
    )

    urlpatterns+=[
        path("home/", include("main.urls")),
        path("", RedirectView.as_view(url="home/", permanent=True)),
        path("accounts/", include("allauth.urls")),
        path("accounts/profile", ProfileView, name="profile"),
        path("accounts/balance", AddBalanceView, name="balanceview"),
        path("accounts/tickets", TicketsView, name="ticketslist"),
        path("accounts/billing", BillingView, name="billing"),
        path("accounts/verification", VerificationView, name="verification"),
        path("accounts/resend-otp", resend_otp, name="resend-otp"),
        path("accounts/refund/<uuid:ticket>", RefundView, name="refund"),
        path("accounts/food/<uuid:ticket>", FoodView, name="food"),
        path("accounts/food/<uuid:ticket>/<uuid:item>", GenOrder, name="genorder"),
        path(
            "accounts/food/<uuid:ticket>/<uuid:order>/<str:operation>",
            AddReduceOrder,
            name="addreduceorder",
        ),
        path("accounts/transactions", TransactionsView, name="transactions"),
        path("logout", LogoutView.as_view()),
        path("panel", panel, name="panel"),
        path("panel/login", adminlogin, name="admin_login"),
        path("panel/logout", adminlogout, name="admin_logout"),
        path("panel/foods", adminfoods, name="admin_foods"),
        path("panel/foods/new", newfood, name="newfood"),
        path("panel/foods/edit/<uuid:foodID>", editfood, name="editfood"),
        path("panel/foods/delete/<uuid:foodID>", refundfood, name="refundfood"),
        path("panel/shows", adminshows, name="admin_shows"),
        path("panel/shows/new", newshow, name="newshow"),
        path("panel/shows/edit/<uuid:showID>", editshow, name="editshow"),
        path("panel/shows/delete/<uuid:showID>", refundshow, name="refundshow"),
    ]
    urlpatterns.extend(static(settings.STATIC_URL, document_root=settings.STATIC_ROOT))