from django.views.decorators.cache import never_cache
from django.shortcuts import render


@never_cache
def home_view(request):
    context = {
        # 'service_categories': ServiceCategory.objects.all()[:6],
        # 'featured_providers': Provider.objects.filter(is_featured=True)[:3],
    }
    return render(request, "core/home.html", context)
