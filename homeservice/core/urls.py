from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('services/', views.services, name='services'),
    path('providers/', views.providers, name='providers'),
    path('book/', views.book_service, name='book_service')
]