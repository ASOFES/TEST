from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from core.models import Vehicule, ActionTraceur
from .models import Entretien
from .forms import EntretienForm

# Fonction pour vérifier si l'utilisateur est admin ou superuser
def is_admin_or_superuser(user):
    return user.is_authenticated and (user.role == 'admin' or user.is_superuser)

@login_required
@user_passes_test(is_admin_or_superuser)
def dashboard(request):
    """Vue pour le tableau de bord du module Entretien"""
    # Récupérer les statistiques
    entretiens_count = Entretien.objects.count()
    entretiens_recents = Entretien.objects.all().order_by('-date_creation')[:5]
    
    # Tracer l'action
    ActionTraceur.objects.create(
        utilisateur=request.user,
        action="Consultation du tableau de bord Entretien",
    )
    
    context = {
        'entretiens_count': entretiens_count,
        'entretiens_recents': entretiens_recents,
    }
    
    return render(request, 'entretien/dashboard.html', context)

@login_required
@user_passes_test(is_admin_or_superuser)
def liste_entretiens(request):
    """Vue pour afficher la liste des entretiens"""
    # Initialiser le queryset
    queryset = Entretien.objects.all()
    
    # Filtres
    vehicule_id = request.GET.get('vehicule')
    statut = request.GET.get('statut')
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    
    # Appliquer les filtres
    if vehicule_id:
        queryset = queryset.filter(vehicule_id=vehicule_id)
    if statut:
        queryset = queryset.filter(statut=statut)
    if date_debut:
        queryset = queryset.filter(date_entretien__gte=date_debut)
    if date_fin:
        queryset = queryset.filter(date_entretien__lte=date_fin)
    
    # Ordonner les résultats
    entretiens = queryset.order_by('-date_entretien')
    
    # Récupérer tous les véhicules pour le filtre
    vehicules = Vehicule.objects.all().order_by('immatriculation')
    
    # Tracer l'action
    ActionTraceur.objects.create(
        utilisateur=request.user,
        action="Consultation de la liste des entretiens",
    )
    
    context = {
        'entretiens': entretiens,
        'vehicules': vehicules,
    }
    
    return render(request, 'entretien/liste_entretiens.html', context)

@login_required
@user_passes_test(is_admin_or_superuser)
def ajouter_entretien(request):
    """Vue pour ajouter un nouvel entretien"""
    if request.method == 'POST':
        form = EntretienForm(request.POST, createur=request.user)
        if form.is_valid():
            entretien = form.save()
            
            # Tracer l'action
            ActionTraceur.objects.create(
                utilisateur=request.user,
                action="Création d'un nouvel entretien",
                details=f"Véhicule: {entretien.vehicule.immatriculation}, Date: {entretien.date_entretien}"
            )
            
            messages.success(request, "L'entretien a été ajouté avec succès.")
            return redirect('entretien:detail_entretien', entretien_id=entretien.id)
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = EntretienForm(createur=request.user)
    
    context = {
        'form': form,
        'title': 'Ajouter un entretien',
    }
    
    return render(request, 'entretien/formulaire_entretien.html', context)

@login_required
@user_passes_test(is_admin_or_superuser)
def detail_entretien(request, entretien_id):
    """Vue pour afficher les détails d'un entretien"""
    entretien = get_object_or_404(Entretien, pk=entretien_id)
    
    # Tracer l'action
    ActionTraceur.objects.create(
        utilisateur=request.user,
        action=f"Consultation des détails de l'entretien #{entretien_id}",
    )
    
    context = {
        'entretien': entretien,
    }
    
    return render(request, 'entretien/detail_entretien.html', context)

@login_required
@user_passes_test(is_admin_or_superuser)
def modifier_entretien(request, entretien_id):
    """Vue pour modifier un entretien existant"""
    entretien = get_object_or_404(Entretien, pk=entretien_id)
    
    if request.method == 'POST':
        form = EntretienForm(request.POST, instance=entretien, createur=request.user)
        if form.is_valid():
            entretien_modifie = form.save()
            
            # Tracer l'action
            ActionTraceur.objects.create(
                utilisateur=request.user,
                action=f"Modification de l'entretien #{entretien_id}",
                details=f"Véhicule: {entretien_modifie.vehicule.immatriculation}, Date: {entretien_modifie.date_entretien}"
            )
            
            messages.success(request, "L'entretien a été modifié avec succès.")
            return redirect('entretien:detail_entretien', entretien_id=entretien.id)
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = EntretienForm(instance=entretien, createur=request.user)
    
    context = {
        'form': form,
        'entretien': entretien,
        'title': 'Modifier un entretien',
    }
    
    return render(request, 'entretien/formulaire_entretien.html', context)

@login_required
@user_passes_test(is_admin_or_superuser)
def supprimer_entretien(request, entretien_id):
    """Vue pour supprimer un entretien"""
    entretien = get_object_or_404(Entretien, pk=entretien_id)
    
    if request.method == 'POST':
        # Tracer l'action
        ActionTraceur.objects.create(
            utilisateur=request.user,
            action=f"Suppression de l'entretien #{entretien_id}",
            details=f"Véhicule: {entretien.vehicule.immatriculation}",
        )
        
        entretien.delete()
        messages.success(request, "L'entretien a été supprimé avec succès.")
        return redirect('entretien:liste_entretiens')
    
    context = {
        'entretien': entretien,
    }
    
    return render(request, 'entretien/confirmer_suppression.html', context)
