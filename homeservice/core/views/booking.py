from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from ..models import Service, Booking, ProviderSchedule, Customer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Avg, Count
import json


@csrf_exempt
@login_required
def unbook_service(request, id): #delete in database
    if request.method == "POST":
        booking = get_object_or_404(Booking, id=id, customer__user=request.user)
        booking.delete()
        return JsonResponse({"message": "Booking has been successfully removed."})
    return JsonResponse({"error": "Only POST requests are allowed."}, status=405)


@login_required
def service_booking(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    provider = service.provider

    if request.method == "POST":
        # Get form data
        date = request.POST.get("date")
        time = request.POST.get("time")
        notes = request.POST.get("notes", "")

        # Validate required fields
        if not date or not time:
            messages.error(
                request, "Please select both date and time for your booking."
            )
            return redirect("service_booking", service_id=service_id)

        try:
            # Get customer
            customer = Customer.objects.get(user=request.user)

            # Create booking
            booking = Booking.objects.create(
                customer=customer,
                service=service,
                booking_date=date,
                booking_time=time,
                notes=notes,
                status="pending",
            )

            from ..models import Notification
            Notification.create_booking_notification(booking)

            messages.success(request, "Your booking has been confirmed successfully!")
            return redirect("profile")  # Or redirect to booking confirmation page

        except Exception as e:
            messages.error(
                request, f"An error occurred while processing your booking: {str(e)}"
            )
            return redirect("service_booking", service_id=service_id)

    # GET request handling (original code)
    schedules = ProviderSchedule.objects.filter(
        provider=provider, is_active=True
    ).order_by("day")

    today = timezone.now().date()
    date_options = [today + timezone.timedelta(days=i) for i in range(30)]

    available_dates = []
    for date_option in date_options:
        day_of_week = date_option.strftime("%A").lower()
        if schedules.filter(day=day_of_week).exists():
            available_dates.append(date_option)

    existing_bookings = Booking.objects.filter(
        service=service, booking_date__in=available_dates
    )

    booked_slots = {}
    for booking in existing_bookings:
        date_str = booking.booking_date.isoformat()
        if date_str not in booked_slots:
            booked_slots[date_str] = []
        booked_slots[date_str].append(booking.booking_time)

    booked_slots_json = json.dumps(booked_slots)
    time_slots_data = {schedule.day: schedule.time_slots for schedule in schedules}
    time_slots_json = json.dumps(time_slots_data)

    review_stats = provider.reviews_received.aggregate(
        average_rating=Avg("rating"), review_count=Count("id")
    )

    average_rating = review_stats["average_rating"] or 0  # Fallback if no reviews
    review_count = review_stats["review_count"]

    context = {
        "service": service,
        "provider": provider,
        "available_dates": available_dates,
        "booked_slots_json": booked_slots_json,
        "time_slots_json": time_slots_json,
        "today": today.isoformat(),
        "average_rating": round(average_rating, 1),
        "review_count": review_count,
        "star_range": range(1, 6),  # Add this line
    }
    return render(request, "core/service_booking.html", context)
