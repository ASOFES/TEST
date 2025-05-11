from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from core.models import Vehicule, Course, ActionTraceur
from entretien.models import Entretien
from ravitaillement.models import Ravitaillement

# Fonction pour vérifier si l'utilisateur est admin ou superuser
def is_admin_or_superuser(user):
    return user.is_authenticated and (user.role == 'admin' or user.is_superuser)

@login_required
@user_passes_test(is_admin_or_superuser)
def dashboard(request):
    """Vue pour le tableau de bord du module Suivi"""
    # Récupérer les statistiques générales
    vehicules_count = Vehicule.objects.count()
    courses_count = Course.objects.count()
    entretiens_count = Entretien.objects.count()
    ravitaillements_count = Ravitaillement.objects.count()
    
    # Tracer l'action
    ActionTraceur.objects.create(
        utilisateur=request.user,
        action="Consultation du tableau de bord Suivi",
    )
    
    context = {
        'vehicules_count': vehicules_count,
        'courses_count': courses_count,
        'entretiens_count': entretiens_count,
        'ravitaillements_count': ravitaillements_count,
    }
    
    return render(request, 'suivi/dashboard.html', context)

@login_required
@user_passes_test(is_admin_or_superuser)
def suivi_vehicules(request):
    """Vue pour le suivi des véhicules"""
    vehicules = Vehicule.objects.all()
    
    # Tracer l'action
    ActionTraceur.objects.create(
        utilisateur=request.user,
        action="Consultation du suivi des véhicules",
    )
    
    context = {
        'vehicules': vehicules,
    }
    
    return render(request, 'suivi/suivi_vehicules.html', context)

@login_required
@user_passes_test(is_admin_or_superuser)
def suivi_missions(request):
    """Vue pour le suivi des missions"""
    courses = Course.objects.all().order_by('-date_demande')
    
    # Tracer l'action
    ActionTraceur.objects.create(
        utilisateur=request.user,
        action="Consultation du suivi des missions",
    )
    
    context = {
        'courses': courses,
    }
    
    return render(request, 'suivi/suivi_missions.html', context)

@login_required
@user_passes_test(is_admin_or_superuser)
def suivi_entretiens(request):
    """Vue pour le suivi des entretiens"""
    entretiens = Entretien.objects.all().order_by('-date_creation')
    
    # Tracer l'action
    ActionTraceur.objects.create(
        utilisateur=request.user,
        action="Consultation du suivi des entretiens",
    )
    
    context = {
        'entretiens': entretiens,
    }
    
    return render(request, 'suivi/suivi_entretiens.html', context)

@login_required
@user_passes_test(is_admin_or_superuser)
def suivi_carburant(request):
    """Vue pour le suivi de la consommation de carburant"""
    ravitaillements = Ravitaillement.objects.all().order_by('-date_creation')
    
    # Tracer l'action
    ActionTraceur.objects.create(
        utilisateur=request.user,
        action="Consultation du suivi de la consommation de carburant",
    )
    
    context = {
        'ravitaillements': ravitaillements,
    }
    
    return render(request, 'suivi/suivi_carburant.html', context)
