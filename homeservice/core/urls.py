from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
import os
from core.views.auth import register, login_view, logout_view, signup_from_home
from core.views.home import home_view
from core.views.profile import profile, delete_profile_image
from core.views.settings import (
    service_settings,
    customer_settings,
    delete_document,
    update_experience,
    add_specialization,
    remove_specialization,
    changePassword,
    deleteAccount,
    updateLocation,
)
from core.views.createService import create_service
from core.views.services import services_view
from core.views.providers import providers_view
from core.views.serviceProvider import service_provider_profile
from core.views.booking import unbook_service, service_booking
from core.views.manageSchedule import manage_schedule
from core.views.serviceDetails import service_details
from core.views.bookings import (
    bookings_view,
    cancel_booking,
    booking_detail_view,
    update_booking_status,
)

urlpatterns = [
    path("", home_view, name="base"),
    path("home/", home_view, name="home"),
    path("register/", register, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("signup_from_home/", signup_from_home, name="signup_from_home"),
    path("profile/", profile, name="profile"),
    path("load_service_settings/", service_settings, name="service_settings"),
    path("load_customer_settings/", customer_settings, name="customer_settings"),
    path("delete_document/", delete_document, name="delete_document"),
    path("update_experience/", update_experience, name="update_experience"),
    path("add_specialization/", add_specialization, name="add_specialization"),
    path(
        "remove_specialization/",
        remove_specialization,
        name="remove_specialization",
    ),
    path(
        "profile/provider_documents/<path:path>",
        serve,
        {"document_root": os.path.join(settings.MEDIA_ROOT, "provider_documents")},
    ),
    path("change_password/", changePassword, name="change_password"),
    path("delete_account/", deleteAccount, name="delete_account"),
    path("delete_profile_image/", delete_profile_image, name="delete_profile_image"),
    path("update_location/", updateLocation, name="update_location"),
    path("create-service/", create_service, name="create_service"),
    path("services/", services_view, name="services"),
    path("providers/", providers_view, name="providers"),
    path(
        "serviceprovider_profile/<int:id>/",
        service_provider_profile,
        name="service_provider_profile",
    ),
    path("unbook_service/<int:id>/", unbook_service, name="book_service"),
    path("service/<int:service_id>/book/", service_booking, name="service_booking"),
    path("manage-schedule/", manage_schedule, name="manage_schedule"),
    path("servicedetails/<int:id>", service_details, name="service_details"),
    path("bookings/", bookings_view, name="bookings"),
    path("cancel_booking/<int:booking_id>/", cancel_booking, name="cancel_booking"),
    path("booking/<int:booking_id>/", booking_detail_view, name="booking_detail"),
    path("update_booking_status/", update_booking_status, name="update_booking_status"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
