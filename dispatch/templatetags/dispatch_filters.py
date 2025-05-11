from django import template

register = template.Library()

@register.filter
def subtract(value, arg):
    """Soustrait l'argument de la valeur."""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return ""
