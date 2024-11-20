from django.contrib import admin

from .models import (
    wallet,
    transactions,
    adminuser,
    foods,
    shows,
    movies,
    user,
    tickets,
    OtpToken,
    foodorder
)

admin.site.register(wallet)
admin.site.register(transactions)
admin.site.register(user)
admin.site.register(adminuser)
admin.site.register(foods)
admin.site.register(shows)
admin.site.register(movies)
admin.site.register(tickets)
admin.site.register(OtpToken)
admin.site.register(foodorder)