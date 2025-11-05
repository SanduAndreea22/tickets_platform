from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('list/', views.events_list, name='events_list'),
    path('<int:pk>/', views.event_detail, name='event_detail'),
]
