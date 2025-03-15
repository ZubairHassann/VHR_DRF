from django import template
from django.db.models import Count

register = template.Library()

@register.filter(name='status_count')
def status_count(queryset, status):
    return queryset.filter(status=status).count()


@register.filter
def multiply(value, arg):
    return value * arg


@register.filter
def sum_scores(responses):
    return sum(response['score'] if response['score'] is not None else 0 for response in responses)