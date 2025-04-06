# In views.py
from django.core.paginator import Paginator
from datetime import date
from ..models import User, Booking, Customer, ServiceProvider
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse

@login_required
def bookings_view(request):
    active_tab = request.GET.get('tab', 'upcoming')
    page_number = request.GET.get('page', 1)
    
    if request.user.role == User.CUSTOMER:
        customer = Customer.objects.get(user=request.user)
        all_bookings = Booking.objects.filter(customer=customer).order_by('-created_at')
        
        # Split into upcoming and past bookings
        upcoming_bookings = all_bookings.filter(
            booking_date__gte=date.today()
        ).exclude(status='cancelled').exclude(status='completed')
        
        past_bookings = all_bookings.filter(
            booking_date__lt=date.today()
        ).exclude(status='cancelled') | all_bookings.filter(
            status__in=['completed', 'cancelled']
        )
        
    elif request.user.role == User.SERVICE_PROVIDER:
        provider = ServiceProvider.objects.get(user=request.user)
        all_bookings = Booking.objects.filter(service__provider=provider).order_by('-created_at')
        
        # Split into upcoming and past bookings
        upcoming_bookings = all_bookings.filter(
            booking_date__gte=date.today()
        ).exclude(status='cancelled').exclude(status='completed')
        
        past_bookings = all_bookings.filter(
            booking_date__lt=date.today()
        ).exclude(status='cancelled') | all_bookings.filter(
            status__in=['completed', 'cancelled']
        )
    
    # Pagination
    if active_tab == 'upcoming':
        paginator = Paginator(upcoming_bookings, 10)
    else:
        paginator = Paginator(past_bookings, 10)
    
    page_obj = paginator.get_page(page_number)
    
    context = {
        'active_tab': active_tab,
        'page_obj': page_obj,
        'is_provider': request.user.role == User.SERVICE_PROVIDER,
    }
    
    return render(request, 'core/bookings.html', context)

# In views.py
@login_required
def cancel_booking(request, booking_id):
    if request.method == 'POST':
        try:
            booking = Booking.objects.get(id=booking_id)
            
            # Check if the user has permission to cancel this booking
            if (request.user.role == User.CUSTOMER and booking.customer.user == request.user) or \
               (request.user.role == User.SERVICE_PROVIDER and booking.service.provider.user == request.user):
                
                booking.status = 'cancelled'
                booking.save()
            
                
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
        except Booking.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Booking not found'}, status=404)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)