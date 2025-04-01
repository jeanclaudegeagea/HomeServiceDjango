from django.urls import path
from . import views

urlpatterns = [
    path("", views.base, name="base"),
    path("home", views.home_view, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile, name="profile"),
    path("customer/dashboard/", views.customer_dashboard, name="customer_dashboard"),
    path("provider/dashboard/", views.provider_dashboard, name="provider_dashboard"),
    # path('provider/upload-docs/', views.provider_upload_docs, name='provider_upload_docs'),
]
