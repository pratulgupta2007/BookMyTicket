from django.shortcuts import render
from django.views import generic
import random
from django.shortcuts import get_object_or_404

# Create your views here.
from .models import wallet, transactions, user, adminuser, foods, shows, movies
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
    context_object_name = 'movie'
    template_name = 'catalog/movie_detail.html'

class TheaterListView(generic.ListView):
    model = adminuser
    context_object_name = 'theaterlist'
    template_name = 'catalog/theater_list.html'

class TheaterDetailView(generic.DetailView):
    model = adminuser
    context_object_name = 'theater'
    template_name = 'catalog/theater_detail.html'
