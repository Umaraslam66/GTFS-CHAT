"""
URL configuration for GTFS Chat project.
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('chat/', views.chat, name='chat'),
    path('health/', views.health_check, name='health'),
]
