from django.shortcuts import render
from django.views import generic
import random
from django.conf import settings
from django.urls import reverse
import datetime
from django.utils import timezone

# Create your views here.
from .models import wallet, transactions,user,  adminuser, foods, shows, movies
def index(request):

    movielist=movies.objects.order_by('movie').values_list('movie').distinct()
    ls=random.sample(range(0, len(movielist)), 3)

    context = {
        'show1': movielist[ls[0]][0],
        'show2': movielist[ls[1]][0],
        'show3': movielist[ls[2]][0],
        'num_theaters': adminuser.objects.all().count(),
        'num_foods': foods.objects.count(),
    }
    return render(request, 'index.html', context=context)

class MoviesListView(generic.ListView):
    model = movies
    context_object_name = 'movielist'
    template_name = 'catalog/movie_list.html'

class MovieDetailView(generic.DetailView):
    model = movies
    def get_context_data(self, **kwargs):
        context = super(MovieDetailView, self).get_context_data(**kwargs)
        showslist=shows.objects.filter(movie_id=context['movies'].movie).filter(date_time__gt=timezone.now())
        context['languages']=showslist.order_by('language').values_list('language', flat=True).distinct()
        context['types']=showslist.order_by('type').values_list('type', flat=True).distinct()
        context['shows']=[[x, ''] for x in showslist.order_by('date_time')]
        for x in context['shows']:
            x[1] = adminuser.objects.filter(theater_name=x[0].get_theatername())[0].get_theater_url()
        return context
    template_name = 'catalog/movie_detail.html'

class TheaterListView(generic.ListView):
    model = adminuser
    context_object_name = 'theaterlist'
    template_name = 'catalog/theater_list.html'

class TheaterDetailView(generic.DetailView):
    model = adminuser
    template_name = 'catalog/theater_detail.html'
    def get_context_data(self, **kwargs):
        context = super(TheaterDetailView, self).get_context_data(**kwargs)
        showslist=shows.objects.filter(adminID=context['adminuser'].aid).filter(date_time__gt=timezone.now())
        context['shows']=[[x, ''] for x in showslist.order_by('date_time')]
        for x in context['shows']:
            x[1] = movies.objects.filter(movie=x[0].get_moviename())[0].get_absolute_url()
        return context

class ShowDetailView(generic.DetailView):
    model=shows
    context_object_name='show'
    template_name='catalog/show_detail.html'
