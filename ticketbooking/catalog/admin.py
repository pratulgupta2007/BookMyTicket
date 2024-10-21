from django.contrib import admin

from .models import wallet, transactions, user, adminuser, foods, shows

admin.site.register(wallet)
admin.site.register(transactions)
admin.site.register(user)
admin.site.register(adminuser)
admin.site.register(foods)
admin.site.register(shows)