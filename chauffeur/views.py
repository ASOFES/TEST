from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from core.models import Course, ActionTraceur
from .forms import DemarrerMissionForm, TerminerMissionForm
import datetime

@login_required
def dashboard(request):
    """Vue pour le tableau de bord du chauffeur"""
    # Vérifier que l'utilisateur est bien un chauffeur
    if request.user.role != 'chauffeur':
        messages.error(request, "Vous n'avez pas les droits pour accéder à cette page.")
        return redirect('home')
    
    # Récupérer les missions assignées au chauffeur connecté avec leurs relations
    missions = Course.objects.select_related('demandeur', 'vehicule', 'dispatcher').filter(chauffeur=request.user).filter(
        Q(statut='validee') | Q(statut='en_cours') | Q(statut='terminee')
    ).order_by('-date_validation')
    
    # Filtres
    statut = request.GET.get('statut')
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    
    if statut:
        missions = missions.filter(statut=statut)
    
    if date_debut:
        date_debut = datetime.datetime.strptime(date_debut, '%Y-%m-%d').date()
        missions = missions.filter(date_validation__date__gte=date_debut)
    
    if date_fin:
        date_fin = datetime.datetime.strptime(date_fin, '%Y-%m-%d').date()
        missions = missions.filter(date_validation__date__lte=date_fin)
    
    # Pagination
    paginator = Paginator(missions, 10)  # 10 missions par page
    page_number = request.GET.get('page')
    missions_page = paginator.get_page(page_number)
    
    # Statistiques
    stats = {
        'total': Course.objects.filter(chauffeur=request.user).count(),
        'a_effectuer': Course.objects.filter(chauffeur=request.user, statut='validee').count(),
        'en_cours': Course.objects.filter(chauffeur=request.user, statut='en_cours').count(),
        'terminees': Course.objects.filter(chauffeur=request.user, statut='terminee').count(),
    }
    
    context = {
        'missions': missions_page,
        'stats': stats,
    }
    
    return render(request, 'chauffeur/dashboard.html', context)

@login_required
def detail_mission(request, mission_id):
    """Vue pour afficher les détails d'une mission"""
    # Vérifier que l'utilisateur est bien un chauffeur
    if request.user.role != 'chauffeur':
        messages.error(request, "Vous n'avez pas les droits pour accéder à cette page.")
        return redirect('home')
    
    mission = get_object_or_404(Course.objects.select_related('demandeur', 'vehicule', 'dispatcher'), id=mission_id, chauffeur=request.user)
    
    # Vérifier que la mission est bien assignée au chauffeur et dans un état valide
    if mission.statut not in ['validee', 'en_cours', 'terminee']:
        messages.error(request, "Vous n'avez pas accès à cette mission.")
        return redirect('chauffeur:dashboard')
    
    # Récupérer l'historique des actions liées à cette mission
    historique = ActionTraceur.objects.filter(
        Q(details__icontains=f"Demande #{mission.id}") |
        Q(details__icontains=f"Course {mission.id}") |
        Q(details__icontains=f"Mission {mission.id}")
    ).order_by('-date_action')
    
    context = {
        'mission': mission,
        'historique': historique,
    }
    
    return render(request, 'chauffeur/detail_mission.html', context)

@login_required
def demarrer_mission(request, mission_id):
    """Vue pour démarrer une mission"""
    # Vérifier que l'utilisateur est bien un chauffeur
    if request.user.role != 'chauffeur':
        messages.error(request, "Vous n'avez pas les droits pour accéder à cette page.")
        return redirect('home')
    
    mission = get_object_or_404(Course, id=mission_id, chauffeur=request.user, statut='validee')
    vehicule = mission.vehicule
    
    if request.method == 'POST':
        form = DemarrerMissionForm(request.POST, vehicule=vehicule)
        if form.is_valid():
            # Mettre à jour la mission
            mission.statut = 'en_cours'
            mission.kilometrage_depart = form.cleaned_data['kilometrage_depart']
            mission.date_depart = timezone.now()
            mission.save()
            
            # Pas besoin de mettre à jour le kilométrage du véhicule car l'attribut n'existe pas
            # Le kilométrage est stocké uniquement dans la course
            
            # Créer une entrée dans l'historique des actions
            commentaire = form.cleaned_data['commentaire']
            action_details = f"Mission {mission.id} démarrée - Kilométrage de départ: {mission.kilometrage_depart} km"
            if commentaire:
                action_details += f" - Commentaire: {commentaire}"
            
            ActionTraceur.objects.create(
                utilisateur=request.user,
                action="Démarrage de mission",
                details=action_details
            )
            
            messages.success(request, f'La mission #{mission.id} a été démarrée avec succès.')
            return redirect('chauffeur:detail_mission', mission.id)
    else:
        # Initialiser le formulaire avec des données vides
        initial_data = {}
        
        form = DemarrerMissionForm(vehicule=vehicule, initial=initial_data)
    
    context = {
        'mission': mission,
        'form': form,
    }
    
    return render(request, 'chauffeur/demarrer_mission.html', context)

@login_required
def terminer_mission(request, mission_id):
    """Vue pour terminer une mission"""
    # Vérifier que l'utilisateur est bien un chauffeur
    if request.user.role != 'chauffeur':
        messages.error(request, "Vous n'avez pas les droits pour accéder à cette page.")
        return redirect('home')
    
    try:
        # Utiliser select_related pour optimiser la requête
        mission = Course.objects.select_related('demandeur', 'vehicule').get(id=mission_id, chauffeur=request.user, statut='en_cours')
    except Course.DoesNotExist:
        # Vérifier si la mission existe mais n'est pas en cours
        try:
            mission_status = Course.objects.values_list('statut', flat=True).get(id=mission_id, chauffeur=request.user)
            messages.error(request, f"La mission #{mission_id} ne peut pas être terminée car son statut actuel est '{mission_status}'")
        except Course.DoesNotExist:
            messages.error(request, f"La mission #{mission_id} n'existe pas ou n'est pas assignée à ce chauffeur.")
        return redirect('chauffeur:dashboard')
    
    if request.method == 'POST':
        form = TerminerMissionForm(request.POST, kilometrage_depart=mission.kilometrage_depart)
        if form.is_valid():
            # Mettre à jour la mission
            mission.statut = 'terminee'
            mission.kilometrage_fin = form.cleaned_data['kilometrage_fin']
            mission.date_fin = timezone.now()
            mission.distance_parcourue = mission.kilometrage_fin - mission.kilometrage_depart
            mission.save()
            
            # Pas besoin de mettre à jour le véhicule car les attributs n'existent pas
            # Le kilométrage est stocké uniquement dans la course
            
            # Créer une entrée dans l'historique des actions
            commentaire = form.cleaned_data['commentaire']
            action_details = f"Mission {mission.id} terminée - Kilométrage d'arrivée: {mission.kilometrage_fin} km - Distance parcourue: {mission.distance_parcourue} km"
            if commentaire:
                action_details += f" - Commentaire: {commentaire}"
            
            ActionTraceur.objects.create(
                utilisateur=request.user,
                action="Fin de mission",
                details=action_details
            )
            
            # Mettre à jour la distance journalière
            from .models import DistanceJournaliere
            date_jour = timezone.now().date()
            distance_jour, created = DistanceJournaliere.objects.get_or_create(
                chauffeur=request.user,
                date=date_jour,
                defaults={
                    'distance_totale': mission.distance_parcourue,
                    'nombre_courses': 1
                }
            )
            
            if not created:
                distance_jour.distance_totale += mission.distance_parcourue
                distance_jour.nombre_courses += 1
                distance_jour.save()
            
            messages.success(request, f'La mission #{mission.id} a été terminée avec succès.')
            return redirect('chauffeur:detail_mission', mission.id)
    else:
        form = TerminerMissionForm(kilometrage_depart=mission.kilometrage_depart)
    
    context = {
        'mission': mission,
        'form': form,
    }
    
    return render(request, 'chauffeur/terminer_mission.html', context)
