from django import template
from django.db.models import Count

register = template.Library()

@register.filter(name='status_count')
def status_count(queryset, status):
    return queryset.filter(status=status).count()


@register.filter
def multiply(value, arg):
    return value * arg


@register.filter(name='split')
def split(value, arg):
    return value.split(arg)