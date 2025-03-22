from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'core/home.html')

def services(request):
    return render(request, 'core/services.html')

def providers(request):
    return render(request, 'core/providers.html')

def book_service(request):
    return render(request, 'core/book_service.html')