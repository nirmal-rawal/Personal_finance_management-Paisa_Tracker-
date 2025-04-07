from django import template
from django.template.defaultfilters import floatformat

register = template.Library()

@register.filter(name='div')
def divide_percentage(value, arg):
    """Divides value by arg and returns percentage"""
    try:
        value = float(value)
        arg = float(arg)
        if arg == 0:
            return 0
        return (value / arg) * 100
    except (ValueError, TypeError):
        return 0

@register.filter(name='divide_percentage')
def divide_percentage_alias(value, arg):
    return divide_percentage(value, arg)