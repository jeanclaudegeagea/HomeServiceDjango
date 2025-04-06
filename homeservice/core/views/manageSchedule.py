from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import (
    User,
    ProviderSchedule,
)
import re

@login_required
def manage_schedule(request):
    if request.user.role != User.SERVICE_PROVIDER:
        return redirect("home")

    provider = request.user.serviceprovider

    if request.method == "POST":

        for day_choice in ProviderSchedule.DAY_CHOICES:
            day = day_choice[0]
            time_slots = request.POST.getlist(f"time_slots_{day}[]")


            if time_slots:

                valid_slots = []
                for slot in time_slots:
                    if re.match(r"^\d{1,2}:\d{2}$", slot):
                        valid_slots.append(slot)


                ProviderSchedule.objects.update_or_create(
                    provider=provider,
                    day=day,
                    defaults={"time_slots": valid_slots, "is_active": bool(valid_slots)},
                )
            else:

                ProviderSchedule.objects.filter(provider=provider, day=day).delete()

        messages.success(request, "Schedule updated successfully!")
        return redirect("manage_schedule")


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