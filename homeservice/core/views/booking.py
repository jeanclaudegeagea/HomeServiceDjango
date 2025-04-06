from ..models import (
    Customer,
    Service,
    Booking,
    ProviderSchedule,
)
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect


@csrf_exempt
@login_required
def unbook_service(request, id):
    if request.method == "POST":
        # Get the service object or return a 404 if not found
        service = get_object_or_404(Service, id=id)
        customer = get_object_or_404(Customer, user=request.user)

        # Get the booking related to the service and the logged-in user
        booking = Booking.objects.filter(service=service, customer=customer).first()

        if booking:
            # Delete the booking from the database
            booking.delete()
            return JsonResponse({"message": "Booking has been successfully removed."})

        return JsonResponse({"error": "No booking found for this service."}, status=404)

    return JsonResponse(
        {"success": False, "message": "Only POST requests are allowed."}
    )


@login_required
def service_booking(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    provider = service.provider

    schedule = ProviderSchedule.objects.filter(provider=provider, is_active=True)

    if request.method == "POST":
        booking_day = request.POST.get("day")
        booking_time = request.POST.get("time")
        notes = request.POST.get("notes", "")

        try:
            day_schedule = schedule.get(day=booking_day)
            if booking_time not in day_schedule.time_slots:
                messages.error(request, "Invalid Time slot selected")
                return redirect("service_booking", service_id=service_id)

            customer = Customer.objects.get(user=request.user)
            Booking.objects.create(
                customer=customer,
                service=service,
                booking_day=booking_day,
                booking_time=booking_time,
                notes=notes,
                status="pending",
            )

            messages.success(request, "Booking request sent successfully!")
            return redirect("service_provdier_profile", id=provider.user.id)

        except ProviderSchedule.DoesNotExist:
            messages.error(request, "Invalid day selected")
            return redirect("service_booking", service_id=service_id)

    context = {"service": service, "provider": provider, "schedule": schedule}
    return render(request, "core/service_booking.html", context)
