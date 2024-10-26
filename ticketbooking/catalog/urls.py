from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('movies/', views.MoviesListView.as_view(), name='movies'),
    path('movies/<slug:slug>', views.MovieDetailView.as_view(), name='movie-detail'),
    path('theaters/', views.TheaterListView.as_view(), name='theaters'),
    path('theaters/<uuid:pk>', views.TheaterDetailView.as_view(), name='theater-detail'),
    path('shows/<uuid:pk>', views.ShowDetailView.as_view(), name='show-detail')
]