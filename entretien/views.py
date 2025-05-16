from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Max, Q
from core.models import Vehicule, ActionTraceur, Course
from .models import Entretien
from .forms import EntretienForm
from core.utils import export_to_pdf, export_to_excel

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
    recherche = request.GET.get('recherche')
    tri = request.GET.get('tri', '-date_entretien')  # Par défaut, tri par date décroissante
    
    # Appliquer les filtres
    if vehicule_id:
        queryset = queryset.filter(vehicule_id=vehicule_id)
    if statut:
        queryset = queryset.filter(statut=statut)
    if date_debut:
        queryset = queryset.filter(date_entretien__gte=date_debut)
    if date_fin:
        queryset = queryset.filter(date_entretien__lte=date_fin)
    if recherche:
        queryset = queryset.filter(
            Q(motif__icontains=recherche) | 
            Q(garage__icontains=recherche) |
            Q(vehicule__immatriculation__icontains=recherche) |
            Q(observations__icontains=recherche)
        )
    
    # Ordonner les résultats selon le critère de tri
    entretiens_list = queryset.order_by(tri)
    
    # Pagination - 5 entretiens par page
    paginator = Paginator(entretiens_list, 5)
    page = request.GET.get('page')
    
    try:
        entretiens = paginator.page(page)
    except PageNotAnInteger:
        # Si la page n'est pas un entier, afficher la première page
        entretiens = paginator.page(1)
    except EmptyPage:
        # Si la page est hors limites, afficher la dernière page
        entretiens = paginator.page(paginator.num_pages)
    
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
        'tri_actuel': tri,
    }
    
    return render(request, 'entretien/liste_entretiens.html', context)

@login_required
@user_passes_test(is_admin_or_superuser)
def ajouter_entretien(request):
    """Vue pour ajouter un nouvel entretien"""
    if request.method == 'POST':
        form = EntretienForm(request.POST, request.FILES, createur=request.user)
        if form.is_valid():
            entretien = form.save()
            
            # Tracer l'action
            details = f"Véhicule: {entretien.vehicule.immatriculation}, Date: {entretien.date_entretien}"
            if entretien.piece_justificative:
                details += f", Pièce justificative ajoutée: {entretien.piece_justificative.name}"
                
            ActionTraceur.objects.create(
                utilisateur=request.user,
                action="Création d'un nouvel entretien",
                details=details
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
        form = EntretienForm(request.POST, request.FILES, instance=entretien, createur=request.user)
        if form.is_valid():
            entretien_modifie = form.save()
            
            # Tracer l'action
            details = f"Véhicule: {entretien_modifie.vehicule.immatriculation}, Date: {entretien_modifie.date_entretien}"
            if 'piece_justificative' in form.changed_data:
                if entretien_modifie.piece_justificative:
                    details += f", Pièce justificative mise à jour: {entretien_modifie.piece_justificative.name}"
                else:
                    details += ", Pièce justificative supprimée"
                    
            ActionTraceur.objects.create(
                utilisateur=request.user,
                action=f"Modification de l'entretien #{entretien_id}",
                details=details
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

@login_required
@user_passes_test(is_admin_or_superuser)
def exporter_entretiens_pdf(request):
    """Vue pour exporter la liste des entretiens en PDF"""
    # Initialiser le queryset
    queryset = Entretien.objects.all()
    
    # Appliquer les filtres comme dans la vue liste_entretiens
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
    
    # Préparer les données pour l'exportation
    data = []
    for entretien in queryset:
        data.append({
            'Véhicule': entretien.vehicule.immatriculation,
            'Garage': entretien.garage,
            'Date': entretien.date_entretien.strftime('%d/%m/%Y'),
            'Motif': entretien.motif,
            'Coût': f"{entretien.cout} $",
            'Statut': entretien.get_statut_display()
        })
    
    # Tracer l'action
    ActionTraceur.objects.create(
        utilisateur=request.user,
        action="Exportation PDF des entretiens",
    )
    
    # Générer le PDF
    return export_to_pdf(
        "Liste des Entretiens", 
        data, 
        "entretiens.pdf",
        user=request.user
    )

@login_required
@user_passes_test(is_admin_or_superuser)
def exporter_entretiens_excel(request):
    """Vue pour exporter la liste des entretiens en Excel"""
    # Initialiser le queryset
    queryset = Entretien.objects.all()
    
    # Appliquer les filtres comme dans la vue liste_entretiens
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
    
    # Préparer les données pour l'exportation
    data = []
    for entretien in queryset:
        data.append({
            'Véhicule': entretien.vehicule.immatriculation,
            'Garage': entretien.garage,
            'Date': entretien.date_entretien.strftime('%d/%m/%Y'),
            'Motif': entretien.motif,
            'Coût': entretien.cout,
            'Statut': entretien.get_statut_display()
        })
    
    # Tracer l'action
    ActionTraceur.objects.create(
        utilisateur=request.user,
        action="Exportation Excel des entretiens",
    )
    
    # Générer le Excel
    return export_to_excel(
        "Liste des Entretiens", 
        data, 
        "entretiens.xlsx"
    )

@login_required
@user_passes_test(is_admin_or_superuser)
def exporter_entretien_pdf(request, entretien_id):
    """Vue pour exporter les détails d'un entretien en PDF"""
    entretien = get_object_or_404(Entretien, pk=entretien_id)
    
    # Préparer les données pour l'exportation
    data = [{
        'Véhicule': entretien.vehicule.immatriculation,
        'Marque/Modèle': f"{entretien.vehicule.marque} {entretien.vehicule.modele}",
        'Garage': entretien.garage,
        'Date': entretien.date_entretien.strftime('%d/%m/%Y'),
        'Statut': entretien.get_statut_display(),
        'Motif': entretien.motif,
        'Coût': f"{entretien.cout} $",
        'Commentaires': entretien.commentaires or "Aucun commentaire"
    }]
    
    # Tracer l'action
    ActionTraceur.objects.create(
        utilisateur=request.user,
        action=f"Exportation PDF de l'entretien #{entretien_id}",
    )
    
    # Générer le PDF
    return export_to_pdf(
        f"Détails de l'Entretien - {entretien.vehicule.immatriculation} ({entretien.date_entretien.strftime('%d/%m/%Y')})", 
        data, 
        f"entretien_{entretien_id}.pdf",
        user=request.user
    )

@login_required
@user_passes_test(is_admin_or_superuser)
def exporter_entretien_excel(request, entretien_id):
    """Vue pour exporter les détails d'un entretien en Excel"""
    entretien = get_object_or_404(Entretien, pk=entretien_id)
    
    # Préparer les données pour l'exportation
    data = [{
        'Véhicule': entretien.vehicule.immatriculation,
        'Marque/Modèle': f"{entretien.vehicule.marque} {entretien.vehicule.modele}",
        'Garage': entretien.garage,
        'Date': entretien.date_entretien.strftime('%d/%m/%Y'),
        'Statut': entretien.get_statut_display(),
        'Motif': entretien.motif,
        'Coût': entretien.cout,
        'Commentaires': entretien.commentaires or "Aucun commentaire"
    }]
    
    # Tracer l'action
    ActionTraceur.objects.create(
        utilisateur=request.user,
        action=f"Exportation Excel de l'entretien #{entretien_id}",
    )
    
    # Générer le Excel
    return export_to_excel(
        f"Détails de l'Entretien - {entretien.vehicule.immatriculation}", 
        data, 
        f"entretien_{entretien_id}.xlsx"
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
        
        # Récupérer la dernière course terminée pour ce véhicule
        derniere_course = Course.objects.filter(
            vehicule=vehicule, 
            statut='terminee'
        ).order_by('-date_fin').first()
        
        # Récupérer également le dernier entretien pour ce véhicule
        dernier_entretien = Entretien.objects.filter(
            vehicule=vehicule
        ).order_by('-date_entretien').first()
        
        # Déterminer le kilométrage le plus récent entre la dernière course et le dernier entretien
        kilometrage_course = derniere_course.kilometrage_fin if derniere_course and derniere_course.kilometrage_fin else 0
        kilometrage_entretien = dernier_entretien.kilometrage if dernier_entretien and dernier_entretien.kilometrage else 0
        
        # Prendre la valeur la plus élevée comme kilométrage actuel
        kilometrage = max(kilometrage_course, kilometrage_entretien)
        
        # Log pour le débogage
        print(f"Kilométrage récupéré pour {vehicule.immatriculation}: {kilometrage} (course: {kilometrage_course}, entretien: {kilometrage_entretien})")
        
        return JsonResponse({
            'success': True,
            'kilometrage': kilometrage,
            'immatriculation': vehicule.immatriculation,
            'source': 'course' if kilometrage_course > kilometrage_entretien else 'entretien' if kilometrage_entretien > kilometrage_course else 'aucune donnée' if kilometrage == 0 else 'égal'
        })
        
    except Vehicule.DoesNotExist:
        return JsonResponse({'error': 'Véhicule non trouvé'}, status=404)
    except Exception as e:
        print(f"Erreur lors de la récupération du kilométrage: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
