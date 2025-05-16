from django import template

register = template.Library()

@register.filter
def index(sequence, position):
    """Retourne l'élément à la position donnée dans une séquence"""
    try:
        return sequence[position]
    except (IndexError, TypeError):
        return None 