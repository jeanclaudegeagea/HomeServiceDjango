from ..models import (
    Service,
    Specialization,
)
from django.db.models import Q
from django.shortcuts import render


def services_view(request):
    # Get all active services
    services = Service.objects.filter(is_active=True).select_related(
        "provider__user", "specialization"
    )

    # Get filter parameters from GET request
    specialization = request.GET.get("specialization")
    search_query = request.GET.get("search")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    location = request.GET.get("location")
    sort = request.GET.get("sort")

    if sort == "price_asc":
        services = services.order_by("price")
    elif sort == "price_desc":
        services = services.order_by("-price")
    elif sort == "name_asc":
        services = services.order_by("name")
    elif sort == "name_desc":
        services = services.order_by("-name")
    elif sort == "created_newest":
        services = services.order_by("-created_at")
    elif sort == "created_oldest":
        services = services.order_by("created_at")

    # Apply filters
    if specialization:
        services = services.filter(specialization__id=specialization)

    if search_query:
        services = services.filter(
            Q(name__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(specialization__name__icontains=search_query)
        )

    if min_price:
        services = services.filter(price__gte=min_price)

    if max_price:
        services = services.filter(price__lte=max_price)

    if location:
        services = services.filter(
            Q(city__icontains=location)
            | Q(state__icontains=location)
            | Q(country__icontains=location)
        )

    # Get all specializations for filter dropdown
    specializations = Specialization.objects.all()

    context = {
        "services": services,
        "specializations": specializations,
        "search_query": search_query or "",
        "selected_specialization": int(specialization) if specialization else "",
        "min_price": min_price or "",
        "max_price": max_price or "",
        "location": location or "",
        "sort": sort or "",
    }

    return render(request, "core/services.html", context)
