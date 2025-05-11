from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def demandeur_required(view_func):
    """Décorateur pour restreindre l'accès aux demandeurs uniquement"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'demandeur':
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
            return redirect('login')
    return _wrapped_view

def dispatcher_required(view_func):
    """Décorateur pour restreindre l'accès aux dispatchers uniquement"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'dispatcher':
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
            return redirect('login')
    return _wrapped_view

def chauffeur_required(view_func):
    """Décorateur pour restreindre l'accès aux chauffeurs uniquement"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'chauffeur':
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
            return redirect('login')
    return _wrapped_view

def securite_required(view_func):
    """Décorateur pour restreindre l'accès au personnel de sécurité uniquement"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'securite':
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
            return redirect('login')
    return _wrapped_view

def admin_required(view_func):
    """Décorateur pour restreindre l'accès aux administrateurs uniquement"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
            return redirect('login')
    return _wrapped_view
