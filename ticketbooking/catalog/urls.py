from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('movies/', views.MoviesListView.as_view(), name='movies'),
    path('movies/<uuid:pk>', views.MovieDetailView.as_view()),
    path('theaters/', views.TheaterListView.as_view(), name='theaters'),
    path('theaters/<uuid:pk>', views.TheaterDetailView.as_view()),
]