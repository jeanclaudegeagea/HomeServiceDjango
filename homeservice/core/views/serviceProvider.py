from ..models import (
    User,
    Customer,
    ServiceProvider,
    Service,
    Booking,
)
from django.shortcuts import render


def service_provider_profile(request, id):
    # Retrieve the service provider related to the given user_id
    service_provider = ServiceProvider.objects.get(user_id=id)

    # Get the years_of_experience and specializations
    years_of_experience = service_provider.years_of_experience
    specializations = service_provider.specialization.all()

    # Get the services provided by this service provider that are active
    services = (
        Service.objects.filter(provider=service_provider, is_active=True)
        .select_related("provider__user", "specialization")
        .order_by("-created_at")
    )

    if request.user.role == User.CUSTOMER:
        # Get the bookings of the user for this service provider
        customer = Customer.objects.get(user=request.user)

        customer_bookings = Booking.objects.filter(
            customer=customer,
        )

        context = {
            "service_provider": service_provider,
            "years_of_experience": years_of_experience,
            "specializations": specializations,
            "services": services,
            "customer_bookings": customer_bookings,  # Pass bookings to the context
        }

    else:
        context = {
            "service_provider": service_provider,
            "years_of_experience": years_of_experience,
            "specializations": specializations,
            "services": services,
        }

    return render(request, "core/service_provider_profile.html", context)
