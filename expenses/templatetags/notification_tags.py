# expenses/templatetags/notification_tags.py
from django import template
from ..models import Notification

register = template.Library()

@register.filter
def unread_notifications(user):
    return Notification.objects.filter(user=user, is_read=False).count()