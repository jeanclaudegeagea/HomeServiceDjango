from django.urls import path
from . import views

urlpatterns = [
    path("", views.base, name="base"),
    path("login", views.login, name="login"),
    path("signup", views.signup, name="signup"),
    path("home", views.home, name="home"),
    path("services", views.services, name="services"),
    path("providers", views.providers, name="providers"),
    path("book", views.book_service, name="book_service"),
]
