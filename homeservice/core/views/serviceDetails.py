from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from ..models import Service  # assuming this is in the same app


@never_cache
@login_required
def service_details(request, id):
    # Get the service object or return 404 if not found
    service = get_object_or_404(Service, id=id, is_active=True)

    provider_specializations = service.provider.specialization.all()

    context = {
        "service": service,  # pass the service object to the template
        "provider_specializations": provider_specializations,
    }

    return render(request, "core/service_details.html", context)
