import re
from django import template

register = template.Library()

@register.filter
def replace(value, arg):
    """
    Remplace une partie d'une chaîne par une autre.
    Usage: {{ value|replace:"pattern,replacement" }}
    """
    pattern, replacement = arg.split(',', 1)
    return re.sub(pattern, replacement, value) 