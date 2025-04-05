from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
import os

urlpatterns = [
    path("", views.home_view, name="base"),
    path("home/", views.home_view, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("signup_from_home/", views.signup_from_home, name="signup_from_home"),
    path("profile/", views.profile, name="profile"),
    path("customer/dashboard/", views.customer_dashboard, name="customer_dashboard"),
    path("provider/dashboard/", views.provider_dashboard, name="provider_dashboard"),
    path("load_service_settings/", views.service_settings, name="service_settings"),
    path("load_customer_settings/", views.customer_settings, name="customer_settings"),
    path("delete_document/", views.delete_document, name="delete_document"),
    path("update_experience/", views.update_experience, name="update_experience"),
    path("add_specialization/", views.add_specialization, name="add_specialization"),
    path(
        "remove_specialization/",
        views.remove_specialization,
        name="remove_specialization",
    ),
    path(
        "profile/provider_documents/<path:path>",
        serve,
        {"document_root": os.path.join(settings.MEDIA_ROOT, "provider_documents")},
    ),
    path("change_password/", views.changePassword, name="change_password"),
    path("delete_account/", views.deleteAccount, name="delete_account"),
    path(
        "delete_profile_image/", views.delete_profile_image, name="delete_profile_image"
    ),
    path("update_location/", views.updateLocation, name="update_location"),
    path("create-service/", views.create_service, name="create_service"),
    path("services/", views.services_view, name="services"),
    path("providers/", views.providers_view, name="providers"),
    path(
        "serviceprovider_profile/<int:id>/",
        views.service_provider_profile,
        name="service_provider_profile",
    ),
    path("book_service/<int:id>/", views.book_service, name="book_service"),
    path("unbook_service/<int:id>/", views.unbook_service, name="book_service"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
