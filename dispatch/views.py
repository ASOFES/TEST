from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum, F, Count, Case, When, Value, IntegerField
from django.utils import timezone
from django.http import HttpResponse
from core.models import Course, ActionTraceur, Utilisateur, Vehicule
from .forms import TraiterDemandeForm
from .utils import export_courses_to_excel, export_course_detail_to_excel
from core.utils import render_to_pdf
import datetime


@login_required
def suivi_kilometrage(request):
    """
    Vue pour le suivi kilométrique des véhicules
    """
    # Récupérer les filtres
    vehicule_id = request.GET.get('vehicule')
    chauffeur_id = request.GET.get('chauffeur')
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    
    # Filtrer les courses avec kilométrage renseigné
    courses = Course.objects.filter(
        Q(kilometrage_depart__isnull=False) | Q(kilometrage_fin__isnull=False),
        statut__in=['en_cours', 'terminee']
    ).select_related('vehicule', 'chauffeur', 'demandeur')
    
    # Appliquer les filtres supplémentaires
    if vehicule_id:
        courses = courses.filter(vehicule_id=vehicule_id)
    
    if chauffeur_id:
        courses = courses.filter(chauffeur_id=chauffeur_id)
    
    if date_debut:
        date_debut = datetime.datetime.strptime(date_debut, '%Y-%m-%d')
        courses = courses.filter(date_depart__date__gte=date_debut)
    
    if date_fin:
        date_fin = datetime.datetime.strptime(date_fin, '%Y-%m-%d')
        courses = courses.filter(date_depart__date__lte=date_fin)
    
    # Récupérer le paramètre de tri
    sort_by = request.GET.get('sort_by', '-date_depart')  # Tri par défaut : date décroissante
    
    # Valider le paramètre de tri pour éviter les injections SQL
    valid_sort_fields = ['date_depart', '-date_depart', 'date_depart__month', '-date_depart__month',
                         'chauffeur__last_name', '-chauffeur__last_name', 
                         'vehicule__immatriculation', '-vehicule__immatriculation', 
                         'distance_parcourue', '-distance_parcourue']
    
    if sort_by not in valid_sort_fields:
        sort_by = '-date_depart'  # Valeur par défaut sécurisée
    
    # Trier les courses selon le paramètre de tri
    courses = courses.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(courses, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistiques par véhicule
    stats_vehicules = courses.values(
        'vehicule__immatriculation', 'vehicule__marque', 'vehicule__modele'
    ).annotate(
        count=Count('id'),
        distance_totale=Sum(Case(
            When(kilometrage_fin__isnull=False, kilometrage_depart__isnull=False, 
                 then=F('kilometrage_fin') - F('kilometrage_depart')),
            default=Value(0),
            output_field=IntegerField()
        ))
    ).filter(vehicule__isnull=False).order_by('-distance_totale')
    
    # Statistiques par chauffeur
    stats_chauffeurs = courses.values('chauffeur').annotate(
        chauffeur_name=F('chauffeur__first_name'),
        count=Count('id'),
        distance_totale=Sum(Case(
            When(kilometrage_fin__isnull=False, kilometrage_depart__isnull=False, 
                 then=F('kilometrage_fin') - F('kilometrage_depart')),
            default=Value(0),
            output_field=IntegerField()
        ))
    ).filter(chauffeur__isnull=False).order_by('-distance_totale')
    
    # Récupérer la liste des véhicules et chauffeurs pour les filtres
    vehicules = Vehicule.objects.all().order_by('immatriculation')
    chauffeurs = Utilisateur.objects.filter(role='chauffeur').order_by('first_name')
    
    context = {
        'courses': page_obj,
        'vehicules': vehicules,
        'chauffeurs': chauffeurs,
        'stats_vehicules': stats_vehicules,
        'stats_chauffeurs': stats_chauffeurs,
        'active_tab': 'suivi'
    }
    
    return render(request, 'dispatch/suivi_kilometrage.html', context)


@login_required
def export_suivi_kilometrage_excel(request):
    """
    Exporte les données de suivi kilométrique au format Excel
    """
    # Récupérer les filtres
    vehicule_id = request.GET.get('vehicule')
    chauffeur_id = request.GET.get('chauffeur')
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    
    # Filtrer les courses avec kilométrage renseigné
    courses = Course.objects.filter(
        Q(kilometrage_depart__isnull=False) | Q(kilometrage_fin__isnull=False),
        statut__in=['en_cours', 'terminee']
    ).select_related('vehicule', 'chauffeur', 'demandeur')
    
    # Appliquer les filtres supplémentaires
    if vehicule_id:
        courses = courses.filter(vehicule_id=vehicule_id)
    
    if chauffeur_id:
        courses = courses.filter(chauffeur_id=chauffeur_id)
    
    if date_debut:
        date_debut = datetime.datetime.strptime(date_debut, '%Y-%m-%d')
        courses = courses.filter(date_depart__date__gte=date_debut)
    
    if date_fin:
        date_fin = datetime.datetime.strptime(date_fin, '%Y-%m-%d')
        courses = courses.filter(date_depart__date__lte=date_fin)
    
    # Créer le nom du fichier avec la date
    filename = f'suivi_kilometrage_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    
    # Utiliser la fonction d'exportation Excel
    return export_courses_to_excel(courses, filename=filename)

@login_required
def dashboard(request):
    """Vue pour le tableau de bord du dispatcher"""
    # Vérifier que l'utilisateur est bien un dispatcher
    if request.user.role != 'dispatch':
        messages.error(request, "Vous n'avez pas les droits pour accéder à cette page.")
        return redirect('home')
    
    # Récupérer toutes les demandes avec les relations
    demandes = Course.objects.select_related('demandeur', 'chauffeur', 'vehicule').all().order_by('-date_demande')
    
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
    paginator = Paginator(demandes, 10)  # 10 demandes par page
    page_number = request.GET.get('page')
    demandes_page = paginator.get_page(page_number)
    
    # Statistiques
    stats = {
        'total': Course.objects.count(),
        'en_attente': Course.objects.filter(statut='en_attente').count(),
        'validees': Course.objects.filter(statut='validee').count(),
        'en_cours': Course.objects.filter(statut='en_cours').count(),
        'terminees': Course.objects.filter(statut='terminee').count(),
        'refusees': Course.objects.filter(statut='refusee').count(),
    }
    
    context = {
        'demandes': demandes_page,
        'stats': stats,
    }
    
    return render(request, 'dispatch/dashboard.html', context)

@login_required
def detail_demande(request, demande_id):
    """Vue pour afficher les détails d'une demande de mission"""
    # Vérifier que l'utilisateur est bien un dispatcher
    if request.user.role != 'dispatch':
        messages.error(request, "Vous n'avez pas les droits pour accéder à cette page.")
        return redirect('home')
    
    demande = get_object_or_404(Course, id=demande_id)
    
    # Récupérer l'historique des actions liées à cette demande
    historique = ActionTraceur.objects.filter(
        Q(details__icontains=f"Demande #{demande.id}") |
        Q(details__icontains=f"Course {demande.id}")
    ).order_by('-date_action')
    
    context = {
        'demande': demande,
        'historique': historique,
    }
    
    return render(request, 'dispatch/detail_demande.html', context)

@login_required
def traiter_demande(request, demande_id):
    """Vue pour traiter une demande de mission"""
    # Vérifier que l'utilisateur est bien un dispatcher
    if request.user.role != 'dispatch':
        messages.error(request, "Vous n'avez pas les droits pour accéder à cette page.")
        return redirect('home')
    
    demande = get_object_or_404(Course, id=demande_id, statut='en_attente')
    
    # Récupérer les chauffeurs disponibles
    chauffeurs = Utilisateur.objects.filter(role='chauffeur', is_active=True)
    
    # Récupérer tous les véhicules
    tous_vehicules = Vehicule.objects.all()
    
    # Filtrer les véhicules disponibles en utilisant la méthode est_disponible
    vehicules = [v for v in tous_vehicules if v.est_disponible()]
    
    if request.method == 'POST':
        form = TraiterDemandeForm(request.POST)
        if form.is_valid():
            decision = form.cleaned_data['decision']
            commentaire = form.cleaned_data['commentaire']
            
            if decision == 'valider':
                # Mettre à jour la demande
                demande.statut = 'validee'
                demande.chauffeur = form.cleaned_data['chauffeur']
                demande.vehicule = form.cleaned_data['vehicule']
                demande.dispatcher = request.user
                demande.date_validation = timezone.now()
                demande.save()
                
                # Le véhicule est maintenant assigné à cette course
                # Pas besoin de mettre à jour un champ de disponibilité car nous filtrons
                # les véhicules disponibles en fonction des courses en cours
                
                # Créer une entrée dans l'historique des actions
                action_details = f"Demande #{demande.id} validée - Chauffeur: {demande.chauffeur.get_full_name()}, Véhicule: {demande.vehicule.immatriculation}"
                if commentaire:
                    action_details += f" - Commentaire: {commentaire}"
                
                ActionTraceur.objects.create(
                    utilisateur=request.user,
                    action="Validation de demande de mission",
                    details=action_details
                )
                
                messages.success(request, f'La demande #{demande.id} a été validée avec succès.')
            else:  # refuser
                demande.statut = 'refusee'
                demande.dispatcher = request.user
                demande.date_validation = timezone.now()
                demande.save()
                
                # Créer une entrée dans l'historique des actions
                action_details = f"Demande #{demande.id} refusée"
                if commentaire:
                    action_details += f" - Motif: {commentaire}"
                
                ActionTraceur.objects.create(
                    utilisateur=request.user,
                    action="Refus de demande de mission",
                    details=action_details
                )
                
                messages.success(request, f'La demande #{demande.id} a été refusée.')
            
            return redirect('dispatch:detail_demande', demande.id)
    else:
        form = TraiterDemandeForm()
    
    context = {
        'demande': demande,
        'form': form,
        'chauffeurs': chauffeurs,
        'vehicules': vehicules,
    }
    
    return render(request, 'dispatch/traiter_demande.html', context)


@login_required
def course_detail_pdf(request, course_id):
    """Vue pour générer un PDF des détails d'une course"""
    # Vérifier que l'utilisateur est bien un dispatcher
    if request.user.role != 'dispatch':
        messages.error(request, "Vous n'avez pas les droits pour accéder à cette page.")
        return redirect('home')
    
    course = get_object_or_404(Course, id=course_id)
    
    # Préparer le contexte pour le template PDF
    context = {
        'course': course,
        'date_impression': timezone.now().strftime('%d/%m/%Y %H:%M'),
        'year': timezone.now().year
    }
    
    # Générer le PDF
    pdf = render_to_pdf('dispatch/pdf/course_detail_pdf.html', context)
    if pdf:
        response = pdf
        filename = f"course_{course_id}_details_{timezone.now().strftime('%Y%m%d')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    return HttpResponse("Une erreur s'est produite lors de la génération du PDF.")


@login_required
def course_detail_excel(request, course_id):
    """Vue pour générer un fichier Excel des détails d'une course"""
    # Vérifier que l'utilisateur est bien un dispatcher
    if request.user.role != 'dispatch':
        messages.error(request, "Vous n'avez pas les droits pour accéder à cette page.")
        return redirect('home')
    
    course = get_object_or_404(Course, id=course_id)
    
    # Générer le fichier Excel
    filename = f"course_{course_id}_details_{timezone.now().strftime('%Y%m%d')}.xlsx"
    return export_course_detail_to_excel(course, filename)


@login_required
def courses_list_pdf(request):
    """Vue pour générer un PDF de la liste des courses avec filtrage"""
    # Vérifier que l'utilisateur est bien un dispatcher
    if request.user.role != 'dispatch':
        messages.error(request, "Vous n'avez pas les droits pour accéder à cette page.")
        return redirect('home')
    
    # Récupérer toutes les demandes avec leurs relations
    courses = Course.objects.select_related('demandeur', 'chauffeur', 'vehicule').all().order_by('-date_demande')
    
    # Appliquer les filtres
    statut = request.GET.get('statut')
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    
    filters = {}
    
    if statut:
        courses = courses.filter(statut=statut)
        filters['statut'] = statut
        # Obtenir l'affichage lisible du statut
        for choice in Course.STATUS_CHOICES:
            if choice[0] == statut:
                filters['statut_display'] = choice[1]
                break
    
    if date_debut:
        date_debut = datetime.datetime.strptime(date_debut, '%Y-%m-%d').date()
        courses = courses.filter(date_demande__date__gte=date_debut)
        filters['date_debut'] = date_debut
    
    if date_fin:
        date_fin = datetime.datetime.strptime(date_fin, '%Y-%m-%d').date()
        courses = courses.filter(date_demande__date__lte=date_fin)
        filters['date_fin'] = date_fin
    
    # Préparer le contexte pour le template PDF
    context = {
        'courses': courses,
        'filters': filters if filters else None,
        'date_impression': timezone.now().strftime('%d/%m/%Y %H:%M'),
        'year': timezone.now().year
    }
    
    # Générer le PDF
    pdf = render_to_pdf('dispatch/pdf/courses_list_pdf.html', context)
    if pdf:
        response = pdf
        filename = f"courses_list_{timezone.now().strftime('%Y%m%d')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    return HttpResponse("Une erreur s'est produite lors de la génération du PDF.")


@login_required
def courses_list_excel(request):
    """Vue pour générer un fichier Excel de la liste des courses avec filtrage"""
    # Vérifier que l'utilisateur est bien un dispatcher
    if request.user.role != 'dispatch':
        messages.error(request, "Vous n'avez pas les droits pour accéder à cette page.")
        return redirect('home')
    
    # Récupérer toutes les demandes avec leurs relations
    courses = Course.objects.select_related('demandeur', 'chauffeur', 'vehicule').all().order_by('-date_demande')
    
    # Appliquer les filtres
    statut = request.GET.get('statut')
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    
    if statut:
        courses = courses.filter(statut=statut)
    
    if date_debut:
        date_debut = datetime.datetime.strptime(date_debut, '%Y-%m-%d').date()
        courses = courses.filter(date_demande__date__gte=date_debut)
    
    if date_fin:
        date_fin = datetime.datetime.strptime(date_fin, '%Y-%m-%d').date()
        courses = courses.filter(date_demande__date__lte=date_fin)
    
    # Générer le fichier Excel
    filename = f"courses_list_{timezone.now().strftime('%Y%m%d')}.xlsx"
    return export_courses_to_excel(courses, filename)
