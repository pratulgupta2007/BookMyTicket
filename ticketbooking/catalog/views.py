from django.shortcuts import render
from django.views import generic
import random
import datetime
from django.shortcuts import get_object_or_404

# Create your views here.
from .models import wallet, transactions, user, adminuser, foods, shows

def index(request):
    ls=random.sample(range(0, shows.objects.all().count()), 3)

    context = {
        'show1': shows.objects.all()[ls[0]],
        'show2': shows.objects.all()[ls[1]],
        'show3': shows.objects.all()[ls[2]],
        'num_theaters': adminuser.objects.all().count(),
        'num_foods': foods.objects.count(),
    }
    return render(request, 'index.html', context=context)

class ShowListView(generic.ListView):
    model = shows
    context_object_name = 'showlist'   # your own name for the list as a template variable

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(ShowListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['time'] = datetime.datetime.now()
        return context

    def get_queryset(self, *args, **kwargs): 
        qs = super(ShowListView, self).get_queryset(*args, **kwargs) 
        qs = qs.order_by("date_time") 
        return qs

    template_name = 'catalog/show_list.html'

def show_detail_view(request, primary_key):
    show = get_object_or_404(shows, pk=primary_key)
    return render(request, 'catalog/show_detail.html', context={'show': show})