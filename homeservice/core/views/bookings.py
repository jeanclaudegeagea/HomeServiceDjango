from django.core.paginator import Paginator
from datetime import date
from ..models import User, Booking, Customer, ServiceProvider
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
import json

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

@login_required
def booking_detail_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Verify the user has permission to view this booking
    if not (request.user == booking.customer.user or 
            (request.user.role == User.SERVICE_PROVIDER and 
             booking.service.provider.user == request.user)):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    context = {
        'booking': booking,
        'status_choices': Booking.STATUS_CHOICES,
    }
    return render(request, 'core/booking_details.html', context)

@login_required
def update_booking_status(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            booking_id = data.get('booking_id')
            new_status = data.get('status')
            
            booking = Booking.objects.get(id=booking_id)
            
            # Verify ownership
            if not (request.user == booking.customer.user or 
                   (request.user.role == User.SERVICE_PROVIDER and 
                    booking.service.provider.user == request.user)):
                return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
            
            # Update booking
            booking.status = new_status
            booking.save()
        
            return JsonResponse({
                'success': True,
                'redirect_url': '/bookings/'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)

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