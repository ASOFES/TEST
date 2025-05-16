from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from core.models import Vehicule, ActionTraceur, Course
from .models import Ravitaillement
from .forms import RavitaillementForm
from core.utils import export_to_pdf, export_to_excel, export_to_pdf_with_image
from django.db.models import Max

# Fonction pour vérifier si l'utilisateur est admin ou superuser
def is_admin_or_superuser(user):
    return user.is_authenticated and (user.role == 'admin' or user.is_superuser)

@login_required
@user_passes_test(is_admin_or_superuser)
def dashboard(request):
    """Vue pour le tableau de bord du module Ravitaillement"""
    # Récupérer les statistiques
    ravitaillements_count = Ravitaillement.objects.count()
    
    # Initialiser le queryset
    queryset = Ravitaillement.objects.all()
    
    # Filtres
    vehicule_id = request.GET.get('vehicule')
    tri = request.GET.get('tri', 'date')
    
    # Appliquer les filtres
    if vehicule_id:
        queryset = queryset.filter(vehicule_id=vehicule_id)
    
    # Appliquer le tri
    if tri == 'date':
        queryset = queryset.order_by('-date_ravitaillement')
    elif tri == 'date_asc':
        queryset = queryset.order_by('date_ravitaillement')
    elif tri == 'vehicule':
        queryset = queryset.order_by('vehicule__immatriculation')
    else:
        queryset = queryset.order_by('-date_ravitaillement')
    
    # Limiter aux 5 derniers ravitaillements pour l'affichage
    ravitaillements_recents = queryset[:5]
    
    # Récupérer tous les véhicules pour le filtre
    vehicules = Vehicule.objects.all().order_by('immatriculation')
    
    # Tracer l'action
    ActionTraceur.objects.create(
        utilisateur=request.user,
        action="Consultation du tableau de bord Ravitaillement",
    )
    
    context = {
        'ravitaillements_count': ravitaillements_count,
        'ravitaillements_recents': ravitaillements_recents,
        'vehicules': vehicules,
        'selected_vehicule': vehicule_id,
        'selected_tri': tri,
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
    
    # Pagination
    page = request.GET.get('page', 1)
    items_per_page = 10  # Nombre d'éléments par page
    paginator = Paginator(queryset, items_per_page)
    
    try:
        ravitaillements_page = paginator.page(page)
    except PageNotAnInteger:
        # Si la page n'est pas un entier, afficher la première page
        ravitaillements_page = paginator.page(1)
    except EmptyPage:
        # Si la page est hors limites (par exemple 9999), afficher la dernière page
        ravitaillements_page = paginator.page(paginator.num_pages)
    
    # Récupérer tous les véhicules pour le filtre
    vehicules = Vehicule.objects.all().order_by('immatriculation')
    
    # Tracer l'action
    ActionTraceur.objects.create(
        utilisateur=request.user,
        action="Consultation de la liste des ravitaillements",
    )
    
    context = {
        'ravitaillements': ravitaillements_page,
        'vehicules': vehicules,
        'page_obj': ravitaillements_page,  # Pour la pagination
    }
    
    return render(request, 'ravitaillement/liste_ravitaillements.html', context)

@login_required
@user_passes_test(is_admin_or_superuser)
def ajouter_ravitaillement(request):
    """Vue pour ajouter un nouveau ravitaillement"""
    if request.method == 'POST':
        form = RavitaillementForm(request.POST, request.FILES, createur=request.user)
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
    ravitaillement = get_object_or_404(Ravitaillement, id=ravitaillement_id)
    
    if request.method == 'POST':
        form = RavitaillementForm(request.POST, request.FILES, instance=ravitaillement, createur=request.user)
        if form.is_valid():
            ravitaillement = form.save()
            
            # Tracer l'action
            ActionTraceur.objects.create(
                utilisateur=request.user,
                action="Modification d'un ravitaillement",
                details=f"Véhicule: {ravitaillement.vehicule.immatriculation}, Litres: {ravitaillement.litres}, Coût: {ravitaillement.cout_total}"
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
        'title': 'Modifier le ravitaillement',
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

@login_required
@user_passes_test(is_admin_or_superuser)
def exporter_ravitaillements_pdf(request):
    """Vue pour exporter la liste des ravitaillements en PDF"""
    # Initialiser le queryset
    queryset = Ravitaillement.objects.all()
    
    # Appliquer les filtres comme dans la vue liste_ravitaillements
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
    elif tri == 'vehicule':
        queryset = queryset.order_by('vehicule__immatriculation')
    else:
        queryset = queryset.order_by('-date_ravitaillement')
    
    # Préparer les données pour l'exportation
    data = []
    for ravitaillement in queryset:
        data.append({
            'Véhicule': ravitaillement.vehicule.immatriculation,
            'Station': ravitaillement.nom_station or 'Non spécifiée',
            'Date': ravitaillement.date_ravitaillement.strftime('%d/%m/%Y %H:%M'),
            'Kilométrage': f"{ravitaillement.kilometrage_apres} km",
            'Distance': f"{ravitaillement.distance_parcourue} km",
            'Litres': f"{ravitaillement.litres} L",
            'Prix unitaire': f"{ravitaillement.cout_unitaire} $/L",
            'Coût total': f"{ravitaillement.cout_total} $",
            'Consommation': f"{ravitaillement.consommation_moyenne:.2f} L/100km" if ravitaillement.consommation_moyenne > 0 else "N/A"
        })
    
    # Tracer l'action
    ActionTraceur.objects.create(
        utilisateur=request.user,
        action="Exportation PDF des ravitaillements",
    )
    
    # Générer le PDF
    return export_to_pdf(
        "Liste des Ravitaillements", 
        data, 
        "ravitaillements.pdf",
        user=request.user
    )

@login_required
@user_passes_test(is_admin_or_superuser)
def exporter_ravitaillements_excel(request):
    """Vue pour exporter la liste des ravitaillements en Excel"""
    # Initialiser le queryset
    queryset = Ravitaillement.objects.all()
    
    # Appliquer les filtres comme dans la vue liste_ravitaillements
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
    elif tri == 'vehicule':
        queryset = queryset.order_by('vehicule__immatriculation')
    else:
        queryset = queryset.order_by('-date_ravitaillement')
    
    # Préparer les données pour l'exportation
    data = []
    for ravitaillement in queryset:
        data.append({
            'Véhicule': ravitaillement.vehicule.immatriculation,
            'Station': ravitaillement.nom_station or 'Non spécifiée',
            'Date': ravitaillement.date_ravitaillement.strftime('%d/%m/%Y %H:%M'),
            'Kilométrage': ravitaillement.kilometrage_apres,
            'Distance': ravitaillement.distance_parcourue,
            'Litres': ravitaillement.litres,
            'Prix unitaire': ravitaillement.cout_unitaire,
            'Coût total': ravitaillement.cout_total,
            'Consommation (L/100km)': round(ravitaillement.consommation_moyenne, 2) if ravitaillement.consommation_moyenne > 0 else "N/A"
        })
    
    # Tracer l'action
    ActionTraceur.objects.create(
        utilisateur=request.user,
        action="Exportation Excel des ravitaillements",
    )
    
    # Générer le Excel
    return export_to_excel(
        "Liste des Ravitaillements", 
        data, 
        "ravitaillements.xlsx"
    )

@login_required
@user_passes_test(is_admin_or_superuser)
def exporter_ravitaillement_pdf(request, ravitaillement_id):
    """Vue pour exporter les détails d'un ravitaillement en PDF"""
    ravitaillement = get_object_or_404(Ravitaillement, pk=ravitaillement_id)
    
    # Préparer les données pour l'exportation
    data = [{
        'Véhicule': ravitaillement.vehicule.immatriculation,
        'Marque/Modèle': f"{ravitaillement.vehicule.marque} {ravitaillement.vehicule.modele}",
        'Station': ravitaillement.nom_station or 'Non spécifiée',
        'Date': ravitaillement.date_ravitaillement.strftime('%d/%m/%Y %H:%M'),
        'Kilométrage avant': f"{ravitaillement.kilometrage_avant} km",
        'Kilométrage après': f"{ravitaillement.kilometrage_apres} km",
        'Distance parcourue': f"{ravitaillement.distance_parcourue} km",
        'Litres': f"{ravitaillement.litres} L",
        'Prix unitaire': f"{ravitaillement.cout_unitaire} $/L",
        'Coût total': f"{ravitaillement.cout_total} $",
        'Consommation': f"{ravitaillement.consommation_moyenne:.2f} L/100km" if ravitaillement.consommation_moyenne > 0 else "N/A",
        'Commentaires': ravitaillement.commentaires or "Aucun commentaire"
    }]
    
    # Tracer l'action
    ActionTraceur.objects.create(
        utilisateur=request.user,
        action=f"Exportation PDF du ravitaillement #{ravitaillement_id}",
    )
    
    # Préparer le chemin de l'image si elle existe
    image_path = None
    if ravitaillement.image:
        image_path = ravitaillement.image.path
    
    # Générer le PDF
    return export_to_pdf_with_image(
        f"Détails du Ravitaillement - {ravitaillement.vehicule.immatriculation} ({ravitaillement.date_ravitaillement.strftime('%d/%m/%Y')})", 
        data, 
        f"ravitaillement_{ravitaillement_id}.pdf",
        image_path=image_path,
        image_caption=f"Reçu pour le ravitaillement du {ravitaillement.date_ravitaillement.strftime('%d/%m/%Y')}",
        user=request.user
    )

@login_required
@user_passes_test(is_admin_or_superuser)
def exporter_ravitaillement_excel(request, ravitaillement_id):
    """Vue pour exporter les détails d'un ravitaillement en Excel"""
    ravitaillement = get_object_or_404(Ravitaillement, pk=ravitaillement_id)
    
    # Préparer les données pour l'exportation
    data = [{
        'Véhicule': ravitaillement.vehicule.immatriculation,
        'Marque/Modèle': f"{ravitaillement.vehicule.marque} {ravitaillement.vehicule.modele}",
        'Station': ravitaillement.nom_station or 'Non spécifiée',
        'Date': ravitaillement.date_ravitaillement.strftime('%d/%m/%Y %H:%M'),
        'Kilométrage avant': ravitaillement.kilometrage_avant,
        'Kilométrage après': ravitaillement.kilometrage_apres,
        'Distance parcourue': ravitaillement.distance_parcourue,
        'Litres': ravitaillement.litres,
        'Prix unitaire': ravitaillement.cout_unitaire,
        'Coût total': ravitaillement.cout_total,
        'Consommation (L/100km)': round(ravitaillement.consommation_moyenne, 2) if ravitaillement.consommation_moyenne > 0 else "N/A",
        'Commentaires': ravitaillement.commentaires or "Aucun commentaire"
    }]
    
    # Tracer l'action
    ActionTraceur.objects.create(
        utilisateur=request.user,
        action=f"Exportation Excel du ravitaillement #{ravitaillement_id}",
    )
    
    # Générer le Excel
    return export_to_excel(
        f"Détails du Ravitaillement - {ravitaillement.vehicule.immatriculation}", 
        data, 
        f"ravitaillement_{ravitaillement_id}.xlsx"
    )

@login_required
@user_passes_test(is_admin_or_superuser)
def get_vehicule_kilometrage(request):
    """API pour récupérer le kilométrage actuel d'un véhicule"""
    vehicule_id = request.GET.get('vehicule_id')
    
    if not vehicule_id:
        return JsonResponse({'error': 'Aucun ID de véhicule fourni'}, status=400)
    
    try:
        vehicule = Vehicule.objects.get(id=vehicule_id)
        
        # Vérifier d'abord le dernier ravitaillement
        dernier_ravitaillement = Ravitaillement.objects.filter(
            vehicule=vehicule
        ).order_by('-date_ravitaillement').first()
        
        # Si un ravitaillement existe, utiliser son kilométrage après
        if dernier_ravitaillement and dernier_ravitaillement.kilometrage_apres > 0:
            kilometrage = dernier_ravitaillement.kilometrage_apres
        else:
            # Sinon, vérifier la dernière course terminée
            derniere_course = Course.objects.filter(
                vehicule=vehicule, 
                statut='terminee'
            ).order_by('-date_fin').first()
            
            kilometrage = derniere_course.kilometrage_fin if derniere_course and derniere_course.kilometrage_fin else 0
        
        return JsonResponse({
            'success': True,
            'kilometrage': kilometrage,
            'immatriculation': vehicule.immatriculation
        })
        
    except Vehicule.DoesNotExist:
        return JsonResponse({'error': 'Véhicule non trouvé'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
