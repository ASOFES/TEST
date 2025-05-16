from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from core.models import Course, ActionTraceur, Utilisateur
from .forms import DemandeForm
from notifications.utils import notify_user, send_sms, send_whatsapp
import datetime

@login_required
def dashboard(request):
    """Vue pour le tableau de bord du demandeur de missions"""
    # Récupérer les demandes de l'utilisateur connecté
    if request.user.role == 'admin' or request.user.is_superuser:
        # Pour les admins et superusers, montrer toutes les demandes
        demandes = Course.objects.all().order_by('-date_demande')
    else:
        # Pour les demandeurs normaux, montrer seulement leurs demandes
        demandes = Course.objects.filter(demandeur=request.user).order_by('-date_demande')
    
    # Filtres
    statut = request.GET.get('statut')
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    
    if statut:
        demandes = demandes.filter(statut=statut)
    
    if date_debut:
        date_debut = datetime.datetime.strptime(date_debut, '%Y-%m-%d').date()
        demandes = demandes.filter(date_demande__date__gte=date_debut)
    
    if date_fin:
        date_fin = datetime.datetime.strptime(date_fin, '%Y-%m-%d').date()
        demandes = demandes.filter(date_demande__date__lte=date_fin)
    
    # Pagination
    paginator = Paginator(demandes, 5)  # 5 demandes par page (réduit de 10 à 5)
    page_number = request.GET.get('page')
    demandes_page = paginator.get_page(page_number)
    
    # Statistiques
    if request.user.role == 'admin' or request.user.is_superuser:
        stats = {
            'total': Course.objects.count(),
            'en_attente': Course.objects.filter(statut='en_attente').count(),
            'validees': Course.objects.filter(statut='validee').count(),
            'refusees': Course.objects.filter(statut='refusee').count(),
        }
    else:
        stats = {
            'total': Course.objects.filter(demandeur=request.user).count(),
            'en_attente': Course.objects.filter(demandeur=request.user, statut='en_attente').count(),
            'validees': Course.objects.filter(demandeur=request.user, statut='validee').count(),
            'refusees': Course.objects.filter(demandeur=request.user, statut='refusee').count(),
        }
    
    context = {
        'demandes': demandes_page,
        'stats': stats,
    }
    
    return render(request, 'demandeur/dashboard.html', context)

@login_required
def nouvelle_demande(request):
    """Vue pour créer une nouvelle demande de mission"""
    if request.method == 'POST':
        form = DemandeForm(request.POST)
        if form.is_valid():
            demande = form.save(commit=False)
            demande.demandeur = request.user
            demande.statut = 'en_attente'
            demande.save()
            
            # Créer une entrée dans l'historique des actions
            ActionTraceur.objects.create(
                utilisateur=request.user,
                action="Création de demande de mission",
                details=f"Demande #{demande.id} - {demande.point_embarquement} → {demande.destination}"
            )
            
            # Notification aux dispatchers
            dispatchers = Utilisateur.objects.filter(role='dispatch', is_active=True)
            
            # Message de notification
            notification_title = f"Nouvelle demande de course #{demande.id}"
            notification_message = f"{request.user.get_full_name()} a créé une nouvelle demande de course de {demande.point_embarquement} à {demande.destination}."
            
            for dispatcher in dispatchers:
                # Notification interne
                notify_user(
                    dispatcher,
                    notification_title,
                    notification_message,
                    notification_type='all',
                    course=demande
                )
                
                # Notification par SMS si le dispatcher a un numéro de téléphone
                if dispatcher.telephone:
                    sms_message = f"{notification_title}\n{notification_message}\nConnectez-vous pour la traiter."
                    send_sms(dispatcher.telephone, sms_message)
                
                # Notification par WhatsApp si le dispatcher a un numéro de téléphone
                if dispatcher.telephone:
                    whatsapp_message = f"*{notification_title}*\n\n{notification_message}\n\nConnectez-vous pour la traiter."
                    send_whatsapp(dispatcher.telephone, whatsapp_message)
            
            messages.success(request, 'Votre demande de mission a été créée avec succès et est en attente de validation.')
            return redirect('demandeur:detail_demande', demande.id)
    else:
        form = DemandeForm()
    
    return render(request, 'demandeur/nouvelle_demande.html', {'form': form})

@login_required
def detail_demande(request, demande_id):
    """Vue pour afficher les détails d'une demande de mission"""
    # Pour les admins et superusers, permettre l'accès à toutes les demandes
    if request.user.role == 'admin' or request.user.is_superuser:
        demande = get_object_or_404(Course, id=demande_id)
    else:
        demande = get_object_or_404(Course, id=demande_id, demandeur=request.user)
    
    # Récupérer l'historique des actions liées à cette demande
    historique = ActionTraceur.objects.filter(
        Q(details__icontains=f"Demande #{demande.id}") |
        Q(details__icontains=f"Course {demande.id}")
    ).order_by('-date_action')
    
    context = {
        'demande': demande,
        'historique': historique,
    }
    
    return render(request, 'demandeur/detail_demande.html', context)

@login_required
def modifier_demande(request, demande_id):
    """Vue pour modifier une demande de mission"""
    # Pour les admins et superusers, permettre l'accès à toutes les demandes
    if request.user.role == 'admin' or request.user.is_superuser:
        demande = get_object_or_404(Course, id=demande_id, statut='en_attente')
    else:
        demande = get_object_or_404(Course, id=demande_id, demandeur=request.user, statut='en_attente')
    
    if request.method == 'POST':
        form = DemandeForm(request.POST, instance=demande)
        if form.is_valid():
            form.save()
            
            # Créer une entrée dans l'historique des actions
            ActionTraceur.objects.create(
                utilisateur=request.user,
                action="Modification de demande de mission",
                details=f"Demande #{demande.id} - {demande.point_embarquement} → {demande.destination}"
            )
            
            messages.success(request, 'Votre demande de mission a été modifiée avec succès.')
            return redirect('demandeur:detail_demande', demande.id)
    else:
        form = DemandeForm(instance=demande)
    
    return render(request, 'demandeur/nouvelle_demande.html', {'form': form, 'demande': demande})

@login_required
def annuler_demande(request, demande_id):
    """Vue pour annuler une demande de mission"""
    # Pour les admins et superusers, permettre l'accès à toutes les demandes
    if request.user.role == 'admin' or request.user.is_superuser:
        demande = get_object_or_404(Course, id=demande_id, statut='en_attente')
    else:
        demande = get_object_or_404(Course, id=demande_id, demandeur=request.user, statut='en_attente')
    
    demande.statut = 'annulee'
    demande.save()
    
    # Créer une entrée dans l'historique des actions
    ActionTraceur.objects.create(
        utilisateur=request.user,
        action="Annulation de demande de mission",
        details=f"Demande #{demande.id} - {demande.point_embarquement} → {demande.destination}"
    )
    
    messages.success(request, 'Votre demande de mission a été annulée avec succès.')
    return redirect('demandeur:dashboard')
