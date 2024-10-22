from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('shows/', views.ShowListView.as_view(), name='shows'),
    #path('shows/<int:pk>', views.show_detail_view.as_view(), name='showdetail'),
]