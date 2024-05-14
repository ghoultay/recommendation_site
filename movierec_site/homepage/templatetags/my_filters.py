# my_filters.py
from django import template

register = template.Library()

@register.filter(name='times') 
def times(number):
    return range(number)

@register.filter
def add(value, arg):
    """
    Adds the value to the argument.
    """
    return value + arg