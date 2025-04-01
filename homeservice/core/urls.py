from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.base, name="base"),
    path("home", views.home_view, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("signup_from_home/", views.signup_from_home, name="signup_from_home"),
    path("profile/", views.profile, name="profile"),
    path("customer/dashboard/", views.customer_dashboard, name="customer_dashboard"),
    path("provider/dashboard/", views.provider_dashboard, name="provider_dashboard"),
    # path('provider/upload-docs/', views.provider_upload_docs, name='provider_upload_docs'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
