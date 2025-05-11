from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from core.models import Vehicule, ActionTraceur
from .models import Ravitaillement
from .forms import RavitaillementForm

# Fonction pour vérifier si l'utilisateur est admin ou superuser
def is_admin_or_superuser(user):
    return user.is_authenticated and (user.role == 'admin' or user.is_superuser)

@login_required
@user_passes_test(is_admin_or_superuser)
def dashboard(request):
    """Vue pour le tableau de bord du module Ravitaillement"""
    # Récupérer les statistiques
    ravitaillements_count = Ravitaillement.objects.count()
    ravitaillements_recents = Ravitaillement.objects.all().order_by('-date_creation')[:5]
    
    # Tracer l'action
    ActionTraceur.objects.create(
        utilisateur=request.user,
        action="Consultation du tableau de bord Ravitaillement",
    )
    
    context = {
        'ravitaillements_count': ravitaillements_count,
        'ravitaillements_recents': ravitaillements_recents,
    }
    
    return render(request, 'ravitaillement/dashboard.html', context)

@login_required
@user_passes_test(is_admin_or_superuser)
def liste_ravitaillements(request):
    """Vue pour afficher la liste des ravitaillements"""
    # Initialiser le queryset
    queryset = Ravitaillement.objects.all()
    
    # Filtres
    vehicule_id = request.GET.get('vehicule')
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    tri = request.GET.get('tri', 'date')
    
    # Appliquer les filtres
    if vehicule_id:
        queryset = queryset.filter(vehicule_id=vehicule_id)
    if date_debut:
        queryset = queryset.filter(date_ravitaillement__date__gte=date_debut)
    if date_fin:
        queryset = queryset.filter(date_ravitaillement__date__lte=date_fin)
    
    # Appliquer le tri
    if tri == 'date':
        queryset = queryset.order_by('-date_ravitaillement')
    elif tri == 'date_asc':
        queryset = queryset.order_by('date_ravitaillement')
    elif tri == 'litres':
        queryset = queryset.order_by('-litres')
    elif tri == 'litres_asc':
        queryset = queryset.order_by('litres')
    elif tri == 'cout':
        queryset = queryset.order_by('-cout_total')
    elif tri == 'cout_asc':
        queryset = queryset.order_by('cout_total')
    else:
        queryset = queryset.order_by('-date_ravitaillement')
    
    # Récupérer tous les véhicules pour le filtre
    vehicules = Vehicule.objects.all().order_by('immatriculation')
    
    # Tracer l'action
    ActionTraceur.objects.create(
        utilisateur=request.user,
        action="Consultation de la liste des ravitaillements",
    )
    
    context = {
        'ravitaillements': queryset,
        'vehicules': vehicules,
    }
    
    return render(request, 'ravitaillement/liste_ravitaillements.html', context)

@login_required
@user_passes_test(is_admin_or_superuser)
def ajouter_ravitaillement(request):
    """Vue pour ajouter un nouveau ravitaillement"""
    if request.method == 'POST':
        form = RavitaillementForm(request.POST, createur=request.user)
        if form.is_valid():
            ravitaillement = form.save()
            
            # Tracer l'action
            ActionTraceur.objects.create(
                utilisateur=request.user,
                action="Création d'un nouveau ravitaillement",
                details=f"Véhicule: {ravitaillement.vehicule.immatriculation}, Litres: {ravitaillement.litres}, Coût: {ravitaillement.cout_total}"
            )
            
            messages.success(request, "Le ravitaillement a été ajouté avec succès.")
            return redirect('ravitaillement:detail_ravitaillement', ravitaillement_id=ravitaillement.id)
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = RavitaillementForm(createur=request.user)
    
    context = {
        'form': form,
        'title': 'Ajouter un ravitaillement',
    }
    
    return render(request, 'ravitaillement/formulaire_ravitaillement.html', context)

@login_required
@user_passes_test(is_admin_or_superuser)
def detail_ravitaillement(request, ravitaillement_id):
    """Vue pour afficher les détails d'un ravitaillement"""
    ravitaillement = get_object_or_404(Ravitaillement, pk=ravitaillement_id)
    
    # Tracer l'action
    ActionTraceur.objects.create(
        utilisateur=request.user,
        action=f"Consultation des détails du ravitaillement #{ravitaillement_id}",
    )
    
    context = {
        'ravitaillement': ravitaillement,
    }
    
    return render(request, 'ravitaillement/detail_ravitaillement.html', context)

@login_required
@user_passes_test(is_admin_or_superuser)
def modifier_ravitaillement(request, ravitaillement_id):
    """Vue pour modifier un ravitaillement existant"""
    ravitaillement = get_object_or_404(Ravitaillement, pk=ravitaillement_id)
    
    if request.method == 'POST':
        form = RavitaillementForm(request.POST, instance=ravitaillement, createur=request.user)
        if form.is_valid():
            ravitaillement_modifie = form.save()
            
            # Tracer l'action
            ActionTraceur.objects.create(
                utilisateur=request.user,
                action=f"Modification du ravitaillement #{ravitaillement_id}",
                details=f"Véhicule: {ravitaillement_modifie.vehicule.immatriculation}, Litres: {ravitaillement_modifie.litres}, Coût: {ravitaillement_modifie.cout_total}"
            )
            
            messages.success(request, "Le ravitaillement a été modifié avec succès.")
            return redirect('ravitaillement:detail_ravitaillement', ravitaillement_id=ravitaillement.id)
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = RavitaillementForm(instance=ravitaillement, createur=request.user)
    
    context = {
        'form': form,
        'ravitaillement': ravitaillement,
        'title': 'Modifier un ravitaillement',
    }
    
    return render(request, 'ravitaillement/formulaire_ravitaillement.html', context)

@login_required
@user_passes_test(is_admin_or_superuser)
def supprimer_ravitaillement(request, ravitaillement_id):
    """Vue pour supprimer un ravitaillement"""
    ravitaillement = get_object_or_404(Ravitaillement, pk=ravitaillement_id)
    
    if request.method == 'POST':
        # Tracer l'action
        ActionTraceur.objects.create(
            utilisateur=request.user,
            action=f"Suppression du ravitaillement #{ravitaillement_id}",
            details=f"Véhicule: {ravitaillement.vehicule.immatriculation}",
        )
        
        ravitaillement.delete()
        messages.success(request, "Le ravitaillement a été supprimé avec succès.")
        return redirect('ravitaillement:liste_ravitaillements')
    
    context = {
        'ravitaillement': ravitaillement,
    }
    
    return render(request, 'ravitaillement/confirmer_suppression.html', context)
