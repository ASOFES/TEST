from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse
from core.models import Vehicule, Course, ActionTraceur
from entretien.models import Entretien
from ravitaillement.models import Ravitaillement

# Fonction pour vérifier si l'utilisateur est admin ou superuser
def is_admin_or_superuser(user):
    return user.is_authenticated and (user.role == 'admin' or user.is_superuser)

@login_required
@user_passes_test(is_admin_or_superuser)
def dashboard(request):
    """Vue pour le tableau de bord du module Rapport"""
    # Tracer l'action
    ActionTraceur.objects.create(
        utilisateur=request.user,
        action="Consultation du tableau de bord Rapport",
    )
    
    context = {
        'title': 'Tableau de bord des rapports',
    }
    
    return render(request, 'rapport/dashboard.html', context)

@login_required
@user_passes_test(is_admin_or_superuser)
def rapport_vehicules(request):
    """Vue pour générer des rapports sur les véhicules"""
    vehicules = Vehicule.objects.all()
    
    # Tracer l'action
    ActionTraceur.objects.create(
        utilisateur=request.user,
        action="Consultation du rapport des véhicules",
    )
    
    context = {
        'vehicules': vehicules,
        'title': 'Rapport des véhicules',
    }
    
    return render(request, 'rapport/rapport_vehicules.html', context)

@login_required
@user_passes_test(is_admin_or_superuser)
def rapport_missions(request):
    """Vue pour générer des rapports sur les missions"""
    courses = Course.objects.all().order_by('-date_demande')
    
    # Tracer l'action
    ActionTraceur.objects.create(
        utilisateur=request.user,
        action="Consultation du rapport des missions",
    )
    
    context = {
        'courses': courses,
        'title': 'Rapport des missions',
    }
    
    return render(request, 'rapport/rapport_missions.html', context)

@login_required
@user_passes_test(is_admin_or_superuser)
def rapport_entretiens(request):
    """Vue pour générer des rapports sur les entretiens"""
    entretiens = Entretien.objects.all().order_by('-date_creation')
    
    # Tracer l'action
    ActionTraceur.objects.create(
        utilisateur=request.user,
        action="Consultation du rapport des entretiens",
    )
    
    context = {
        'entretiens': entretiens,
        'title': 'Rapport des entretiens',
    }
    
    return render(request, 'rapport/rapport_entretiens.html', context)

@login_required
@user_passes_test(is_admin_or_superuser)
def rapport_carburant(request):
    """Vue pour générer des rapports sur la consommation de carburant"""
    ravitaillements = Ravitaillement.objects.all().order_by('-date_creation')
    
    # Tracer l'action
    ActionTraceur.objects.create(
        utilisateur=request.user,
        action="Consultation du rapport de consommation de carburant",
    )
    
    context = {
        'ravitaillements': ravitaillements,
        'title': 'Rapport de consommation de carburant',
    }
    
    return render(request, 'rapport/rapport_carburant.html', context)

@login_required
@user_passes_test(is_admin_or_superuser)
def generer_rapport(request, type_rapport):
    """Vue pour générer un rapport au format PDF ou Excel"""
    # Logique pour générer le rapport en fonction du type (PDF, Excel, etc.)
    # Cette fonction est un placeholder pour l'instant
    
    # Tracer l'action
    ActionTraceur.objects.create(
        utilisateur=request.user,
        action=f"Génération d'un rapport {type_rapport}",
    )
    
    messages.success(request, f"Le rapport {type_rapport} a été généré avec succès.")
    
    # Rediriger vers la page appropriée en fonction du type de rapport
    if type_rapport == 'vehicules':
        return redirect('rapport:rapport_vehicules')
    elif type_rapport == 'missions':
        return redirect('rapport:rapport_missions')
    elif type_rapport == 'entretiens':
        return redirect('rapport:rapport_entretiens')
    elif type_rapport == 'carburant':
        return redirect('rapport:rapport_carburant')
    else:
        return redirect('rapport:dashboard')
