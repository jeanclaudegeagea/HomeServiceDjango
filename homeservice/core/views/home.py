from django.views.decorators.cache import never_cache
from django.shortcuts import render


@never_cache
def home_view(request):
    return render(request, "core/home.html")
