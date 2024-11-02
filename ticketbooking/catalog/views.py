from django.views import generic
import random
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
import json
import uuid

# Create your views here.
from .models import wallet, transactions,user,  adminuser, foods, shows, movies, tickets
from .forms import TicketForm, BillingForm
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

@login_required
def ShowDetailView(request, pk):
    error=None
    show=shows.objects.get(pk=pk)
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            data=form.cleaned_data['ticket_no']
            if timezone.now()>show.date_time:
                error='Show date passed'
            elif data>show.availableseats():
                error='Seats not available'
            else:
                tempticket=json.dumps({'count': str(data), 'show':str(show.showID), 'user':str(request.user), 'price':str(show.price)})
                request.session['tempticket']=tempticket
                return HttpResponseRedirect(reverse('billing'))
    else:
        form = TicketForm()

    context={'show': show, 'form': form, 'error': error}
    return render(request, 'catalog/show_detail.html', context=context)

@login_required
def ProfileView(request):
    context={'balance': user.objects.filter(user=(request.user))[0].walletid.balance}
    return render(request, 'account/profile.html', context=context)

@login_required
def AddBalanceView(request):
    return render(request, 'account/balance.html')

@login_required
def TicketsView(request):
    ticketlist=tickets.objects.filter(user=(request.user))

    context={'tickets': ticketlist}
    return render(request, 'account/ticketslist.html', context=context)

@login_required
def BillingView(request):
    tempticket=json.loads(request.session['tempticket'])
    if tempticket['user']==str(request.user):
        temp={'count': int(tempticket['count']), 'show':shows.objects.get(pk=uuid.UUID(tempticket['show'])), 'price':float(tempticket['price'])}
        context=temp
        context['total']=context['count']*context['price']
        if context['total']>user.objects.filter(user=(request.user))[0].walletid.balance:
            context['error']='Insufficient balance.'
        else:
            if request.method == 'POST':
                form = BillingForm(request.POST)
                if form.is_valid():
                    return HttpResponseRedirect(reverse('profile'))
            else:
                form = BillingForm()
            context['form']=form
    return render(request, 'account/billing.html', context=context)