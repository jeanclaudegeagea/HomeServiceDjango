from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..models import Notification

@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()

    if notifications.filter(is_read=False).exists():
        notifications.filter(is_read=False).update(is_read=True)

    context = {
        'notifications': notifications,
        'unread_count': unread_count
    }

    return render(request, 'core/notifications.html', context)