from django.shortcuts import render


def how_it_works(request):
    # Determine active tab from query parameter
    active_tab = request.GET.get("tab", "customer")
    if active_tab not in ["customer", "provider"]:
        active_tab = "customer"

    context = {"active_tab": active_tab}
    return render(request, "core/how_it_works.html", context)
