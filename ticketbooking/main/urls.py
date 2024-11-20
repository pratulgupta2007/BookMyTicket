from django.urls import path, include
from . import views


from .accounts_views import (
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
from .panel_views import (
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

urlpatterns = [
    path("home/", views.index, name="index"),
    path("home/movies/", views.MoviesListView.as_view(), name="movies"),
    path("home/movies/<slug:slug>", views.MovieDetailView.as_view(), name="movie-detail"),
    path("home/theaters/", views.TheaterListView.as_view(), name="theaters"),
    path(
        "home/theaters/<uuid:pk>", views.TheaterDetailView.as_view(), name="theater-detail"
    ),
    path("home/shows/<uuid:pk>", views.ShowDetailView, name="show-detail"),

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
