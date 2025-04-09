from django.shortcuts import render, redirect
from ..forms import ServiceForm, User
from django.contrib import messages
from django.contrib.auth.decorators import login_required


@login_required
def create_service(request):
    if request.user.role != User.SERVICE_PROVIDER:
        return redirect("home")

    if request.method == "POST":
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.provider = request.user.serviceprovider
            service.save()
            messages.success(request, "Service created successfully!")
            return redirect("create_service")
    else:
        form = ServiceForm()

    return render(request, "core/create_service.html", {"form": form})
