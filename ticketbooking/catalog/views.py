from django.shortcuts import render
import random

# Create your views here.
from .models import wallet, transactions, user, adminuser, foods, shows

def index(request):

    numshows=shows.objects.all().count()
    ls=random.sample(range(0, numshows), 3)

    context = {
        'show1': shows.objects.order_by('-movie')[ls[0]],
        'show2': shows.objects.order_by('-movie')[ls[1]],
        'show3': shows.objects.order_by('-movie')[ls[2]],
        'num_theaters': adminuser.objects.all().count(),
        'num_foods': foods.objects.count(),
    }
    return render(request, 'index.html', context=context)
