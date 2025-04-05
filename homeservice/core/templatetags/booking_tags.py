# booking_tags.py
from django import template

register = template.Library()

@register.filter(name="filter_booking_for_service")
def filter_booking_for_service(customer_bookings, service_id):
    """Check if any booking matches the given service ID."""
    return any(booking.service_id == service_id for booking in customer_bookings)