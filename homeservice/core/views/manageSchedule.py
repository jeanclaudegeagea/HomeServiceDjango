from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import (
    User,
    ProviderSchedule,
)
import re


# views.py
@login_required
def manage_schedule(request):
    if request.user.role != User.SERVICE_PROVIDER:
        return redirect("home")

    provider = request.user.serviceprovider
    weekly_schedule, created = ProviderSchedule.objects.get_or_create(
        provider=provider, defaults={"day": "monday", "time_slots": []}
    )

    if request.method == "POST":
        day = request.POST.get("day")
        time_slots = request.POST.getlist("time_slots[]")

        # Validate time slots format
        valid_slots = []
        for slot in time_slots:
            if re.match(r"^\d{1,2}:\d{2}$", slot):
                valid_slots.append(slot)

        # Update or create schedule for the day
        schedule, created = ProviderSchedule.objects.update_or_create(
            provider=provider,
            day=day,
            defaults={"time_slots": valid_slots, "is_active": bool(valid_slots)},
        )

        messages.success(
            request, f"Schedule for {schedule.get_day_display()} updated successfully!"
        )
        return redirect("manage_schedule")

    # Get all days, even if not created yet
    days = []
    for day_choice in ProviderSchedule.DAY_CHOICES:
        day = day_choice[0]
        try:
            schedule = ProviderSchedule.objects.get(provider=provider, day=day)
        except ProviderSchedule.DoesNotExist:
            schedule = ProviderSchedule(provider=provider, day=day, time_slots=[])
        days.append(schedule)

    context = {
        "days": days,
    }
    return render(request, "serviceProvider/schedule.html", context)
