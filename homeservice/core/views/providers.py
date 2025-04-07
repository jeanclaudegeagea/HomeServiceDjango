from ..models import ServiceProvider, Specialization, User
from django.db.models import Count, Q
from django.shortcuts import render


def providers_view(request):
    # Get all active service providers with their services count
    providers = ServiceProvider.objects.filter(user__is_active=True).annotate(
        service_count=Count("service", filter=Q(service__is_active=True))
    )

    # Check if the user has the 'role' attribute and if it's a 'Service_Provider'
    if hasattr(request.user, "role"):
        if request.user.role == User.SERVICE_PROVIDER:
            # If the user is a service provider, place them first in the list
            providers = providers.annotate(
                is_current_user=Q(
                    user=request.user
                )  # Custom annotation to check if it's the current user
            )
            providers = providers.order_by(
                "-is_current_user", "user__first_name"
            )  # Sort with current user first
        else:
            providers = providers.order_by("user__first_name")
    else:
        # Default order for others
        providers = providers.order_by("user__first_name")

    # Get filter parameters from GET request
    specialization = request.GET.get("specialization")
    search_query = request.GET.get("search")
    min_experience = request.GET.get("min_experience")
    location = request.GET.get("location")

    # Apply filters
    if specialization:
        providers = providers.filter(specialization__id=specialization)

    if search_query:
        providers = providers.filter(
            Q(user__first_name__icontains=search_query)
            | Q(user__last_name__icontains=search_query)
            | Q(specialization__name__icontains=search_query)
        )

    if min_experience:
        providers = providers.filter(years_of_experience__gte=min_experience)

    if location:
        providers = providers.filter(
            Q(service__city__icontains=location)
            | Q(service__state__icontains=location)
            | Q(service__country__icontains=location)
        ).distinct()

    # Get all specializations for filter dropdown
    specializations = Specialization.objects.all()

    context = {
        "providers": providers,
        "specializations": specializations,
        "search_query": search_query or "",
        "selected_specialization": int(specialization) if specialization else "",
        "min_experience": min_experience or "",
        "location": location or "",
    }

    return render(request, "core/providers.html", context)
