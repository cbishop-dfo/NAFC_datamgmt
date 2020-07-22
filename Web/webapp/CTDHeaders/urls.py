#from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='Header_Homepage'),
    path('CTD_Map', views.map, name='CTD_Map'),
]
