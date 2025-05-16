from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Sum, Count, Q, F, Max
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from core.models import Vehicule, Course, ActionTraceur, Utilisateur
from entretien.models import Entretien
from ravitaillement.models import Ravitaillement
from core.utils import export_to_pdf, export_to_excel

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
    vehicules_list = Vehicule.objects.all().order_by('immatriculation')
    
    # Pagination - 10 véhicules par page
    paginator = Paginator(vehicules_list, 10)
    page = request.GET.get('page')
    
    try:
        vehicules = paginator.page(page)
    except PageNotAnInteger:
        # Si la page n'est pas un entier, afficher la première page
        vehicules = paginator.page(1)
    except EmptyPage:
        # Si la page est hors limites (par exemple 9999), afficher la dernière page
        vehicules = paginator.page(paginator.num_pages)
    
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
    # Initialiser le queryset avec select_related pour charger les relations
    queryset = Course.objects.all().select_related('vehicule', 'chauffeur', 'demandeur')
    
    # Appliquer les filtres
    vehicule_id = request.GET.get('vehicule')
    chauffeur_id = request.GET.get('chauffeur')
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    statut = request.GET.get('statut')
    
    if vehicule_id:
        queryset = queryset.filter(vehicule_id=vehicule_id)
    if chauffeur_id:
        queryset = queryset.filter(chauffeur_id=chauffeur_id)
    if date_debut:
        queryset = queryset.filter(date_demande__date__gte=date_debut)
    if date_fin:
        queryset = queryset.filter(date_demande__date__lte=date_fin)
    if statut:
        queryset = queryset.filter(statut=statut)
    
    # Trier par date de demande (plus récent en premier)
    courses_list = queryset.order_by('-date_demande')
    
    # Pagination - 2 missions par page (pour test)
    paginator = Paginator(courses_list, 2)
    page = request.GET.get('page')
    
    try:
        courses = paginator.page(page)
    except PageNotAnInteger:
        # Si la page n'est pas un entier, afficher la première page
        courses = paginator.page(1)
    except EmptyPage:
        # Si la page est hors limites (par exemple 9999), afficher la dernière page
        courses = paginator.page(paginator.num_pages)
    
    # Récupérer tous les véhicules pour le filtre
    vehicules = Vehicule.objects.all().order_by('immatriculation')
    
    # Récupérer tous les chauffeurs pour le filtre
    chauffeurs = Utilisateur.objects.filter(role='chauffeur').order_by('first_name', 'last_name')
    
    # Tracer l'action
    ActionTraceur.objects.create(
        utilisateur=request.user,
        action="Consultation du rapport des missions",
    )
    
    context = {
        'courses': courses,
        'vehicules': vehicules,
        'chauffeurs': chauffeurs,
        'title': 'Rapport des missions',
    }
    
    return render(request, 'rapport/rapport_missions.html', context)

@login_required
@user_passes_test(is_admin_or_superuser)
def rapport_entretiens(request):
    """Vue pour générer des rapports sur les entretiens"""
    # Initialiser le queryset
    queryset = Entretien.objects.all()
    
    # Appliquer les filtres
    vehicule_id = request.GET.get('vehicule')
    type_entretien = request.GET.get('type_entretien')
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    statut = request.GET.get('statut')
    
    if vehicule_id:
        queryset = queryset.filter(vehicule_id=vehicule_id)
    if type_entretien:
        queryset = queryset.filter(type_entretien=type_entretien)
    if date_debut:
        queryset = queryset.filter(date_creation__date__gte=date_debut)
    if date_fin:
        queryset = queryset.filter(date_creation__date__lte=date_fin)
    if statut:
        queryset = queryset.filter(statut=statut)
    
    # Trier par date de création (plus récent en premier)
    entretiens_list = queryset.order_by('-date_creation')
    
    # Calculer le coût total des entretiens filtrés
    cout_total = entretiens_list.aggregate(Sum('cout'))['cout__sum'] or 0
    
    # Pagination - 2 entretiens par page (pour test)
    paginator = Paginator(entretiens_list, 2)
    page = request.GET.get('page')
    
    try:
        entretiens = paginator.page(page)
    except PageNotAnInteger:
        # Si la page n'est pas un entier, afficher la première page
        entretiens = paginator.page(1)
    except EmptyPage:
        # Si la page est hors limites (par exemple 9999), afficher la dernière page
        entretiens = paginator.page(paginator.num_pages)
    
    # Récupérer tous les véhicules pour le filtre
    vehicules = Vehicule.objects.all().order_by('immatriculation')
    
    # Tracer l'action
    ActionTraceur.objects.create(
        utilisateur=request.user,
        action="Consultation du rapport des entretiens",
    )
    
    context = {
        'entretiens': entretiens,
        'vehicules': vehicules,
        'cout_total': cout_total,
        'title': 'Rapport des entretiens',
    }
    
    return render(request, 'rapport/rapport_entretiens.html', context)

@login_required
@user_passes_test(is_admin_or_superuser)
def rapport_carburant(request):
    """Vue pour générer des rapports sur la consommation de carburant"""
    # Initialiser le queryset
    queryset = Ravitaillement.objects.all()
    
    # Appliquer les filtres
    vehicule_id = request.GET.get('vehicule')
    station = request.GET.get('station')
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    montant_min = request.GET.get('montant_min')
    
    if vehicule_id:
        queryset = queryset.filter(vehicule_id=vehicule_id)
    if station:
        queryset = queryset.filter(nom_station__icontains=station)
    if date_debut:
        queryset = queryset.filter(date_ravitaillement__date__gte=date_debut)
    if date_fin:
        queryset = queryset.filter(date_ravitaillement__date__lte=date_fin)
    if montant_min:
        queryset = queryset.filter(cout_total__gte=montant_min)
    
    # Trier par date de ravitaillement (plus récent en premier)
    ravitaillements_list = queryset.order_by('-date_ravitaillement')
    
    # Calculer les totaux
    total_litres = ravitaillements_list.aggregate(Sum('litres'))['litres__sum'] or 0
    total_cout = ravitaillements_list.aggregate(Sum('cout_total'))['cout_total__sum'] or 0
    
    # Pagination - 2 ravitaillements par page (pour test)
    paginator = Paginator(ravitaillements_list, 2)
    page = request.GET.get('page')
    
    try:
        ravitaillements = paginator.page(page)
    except PageNotAnInteger:
        # Si la page n'est pas un entier, afficher la première page
        ravitaillements = paginator.page(1)
    except EmptyPage:
        # Si la page est hors limites (par exemple 9999), afficher la dernière page
        ravitaillements = paginator.page(paginator.num_pages)
    
    # Récupérer tous les véhicules pour le filtre
    vehicules = Vehicule.objects.all().order_by('immatriculation')
    
    # Tracer l'action
    ActionTraceur.objects.create(
        utilisateur=request.user,
        action="Consultation du rapport de consommation de carburant",
    )
    
    context = {
        'ravitaillements': ravitaillements,
        'vehicules': vehicules,
        'total_litres': total_litres,
        'total_cout': total_cout,
        'title': 'Rapport de consommation de carburant',
    }
    
    return render(request, 'rapport/rapport_carburant.html', context)

@login_required
@user_passes_test(is_admin_or_superuser)
def generer_rapport(request, type_rapport):
    """Vue pour générer un rapport au format PDF ou Excel"""
    # Logique pour générer le rapport en fonction du type (PDF, Excel, etc.)
    
    # Tracer l'action
    ActionTraceur.objects.create(
        utilisateur=request.user,
        action=f"Génération d'un rapport {type_rapport}",
    )
    
    if type_rapport == 'entretiens':
        # Récupérer les mêmes filtres que dans la vue rapport_entretiens
        queryset = Entretien.objects.all()
        
        vehicule_id = request.GET.get('vehicule')
        type_entretien = request.GET.get('type_entretien')
        date_debut = request.GET.get('date_debut')
        date_fin = request.GET.get('date_fin')
        statut = request.GET.get('statut')
        
        if vehicule_id:
            queryset = queryset.filter(vehicule_id=vehicule_id)
        if type_entretien:
            queryset = queryset.filter(type_entretien=type_entretien)
        if date_debut:
            queryset = queryset.filter(date_creation__date__gte=date_debut)
        if date_fin:
            queryset = queryset.filter(date_creation__date__lte=date_fin)
        if statut:
            queryset = queryset.filter(statut=statut)
        
        entretiens = queryset.order_by('-date_creation')
        
        # Calculer le coût total des entretiens filtrés
        cout_total = entretiens.aggregate(Sum('cout'))['cout__sum'] or 0
        
        # Préparer les données pour l'exportation
        data = []
        for entretien in entretiens:
            data.append({
                'ID': entretien.id,
                'Date': entretien.date_creation.strftime('%d/%m/%Y'),
                'Véhicule': entretien.vehicule.immatriculation,
                'Marque/Modèle': f"{entretien.vehicule.marque} {entretien.vehicule.modele}",
                'Type': entretien.motif,
                'Garage': entretien.garage or 'Non spécifié',
                'Coût': f"{entretien.cout} $",
                'Kilométrage': "N/A",  # Nous n'avons pas cette information dans le modèle Entretien
                'Statut': dict(Entretien.STATUS_CHOICES).get(entretien.statut, entretien.statut),
                'Description': entretien.commentaires or 'Aucune description'
            })
        
        # Ajouter une ligne de total pour le coût
        data.append({
            'ID': '',
            'Date': 'TOTAL',
            'Véhicule': '',
            'Marque/Modèle': '',
            'Type': '',
            'Garage': '',
            'Coût': f"{cout_total} $",
            'Kilométrage': '',
            'Statut': '',
            'Description': ''
        })
        
        # Générer le rapport au format demandé
        format_export = request.GET.get('format', 'pdf')
        
        if format_export == 'excel':
            # Générer un rapport Excel
            return export_to_excel(
                "Rapport des entretiens", 
                data, 
                "rapport_entretiens.xlsx"
            )
        else:
            # Générer un rapport PDF par défaut
            return export_to_pdf(
                "Rapport des entretiens", 
                data, 
                "rapport_entretiens.pdf",
                user=request.user
            )
    
    elif type_rapport == 'vehicules':
        # Récupérer les données des véhicules
        vehicules = Vehicule.objects.all()
        
        # Préparer les données pour l'exportation
        data = []
        for vehicule in vehicules:
            data.append({
                'Immatriculation': vehicule.immatriculation,
                'Marque/Modèle': f"{vehicule.marque} {vehicule.modele}",
                'Année': vehicule.annee,
                'Kilométrage': f"{vehicule.kilometrage_actuel} km",
                'Statut': 'Actif' if vehicule.est_actif else 'Inactif',
                'Dernière maintenance': vehicule.date_derniere_maintenance.strftime('%d/%m/%Y') if vehicule.date_derniere_maintenance else 'Non disponible',
                'Consommation moyenne': f"{vehicule.consommation_moyenne:.2f} L/100km" if vehicule.consommation_moyenne else 'Non disponible'
            })
        
        # Générer le rapport au format demandé
        format_export = request.GET.get('format', 'pdf')
        
        if format_export == 'excel':
            return export_to_excel(
                "Rapport des véhicules", 
                data, 
                "rapport_vehicules.xlsx"
            )
        else:
            return export_to_pdf(
                "Rapport des véhicules", 
                data, 
                "rapport_vehicules.pdf",
                user=request.user
            )
    
    elif type_rapport == 'missions':
        # Récupérer les données des missions avec filtres
        queryset = Course.objects.all().select_related('vehicule', 'chauffeur', 'demandeur')
        
        # Appliquer les filtres
        vehicule_id = request.GET.get('vehicule')
        chauffeur_id = request.GET.get('chauffeur')
        date_debut = request.GET.get('date_debut')
        date_fin = request.GET.get('date_fin')
        statut = request.GET.get('statut')
        
        if vehicule_id:
            queryset = queryset.filter(vehicule_id=vehicule_id)
        if chauffeur_id:
            queryset = queryset.filter(chauffeur_id=chauffeur_id)
        if date_debut:
            queryset = queryset.filter(date_demande__date__gte=date_debut)
        if date_fin:
            queryset = queryset.filter(date_demande__date__lte=date_fin)
        if statut:
            queryset = queryset.filter(statut=statut)
        
        # Trier par date de demande (plus récent en premier)
        courses = queryset.order_by('-date_demande')
        
        # Préparer les données pour l'exportation
        data = []
        for course in courses:
            # S'assurer que le demandeur existe
            demandeur_nom = "Non assigné"
            if course.demandeur:
                if course.demandeur.first_name or course.demandeur.last_name:
                    demandeur_nom = f"{course.demandeur.first_name} {course.demandeur.last_name}".strip()
                else:
                    demandeur_nom = course.demandeur.username
                
            data.append({
                'ID': course.id,
                'Date': course.date_demande.strftime('%d/%m/%Y %H:%M'),
                'Véhicule': course.vehicule.immatriculation if course.vehicule else 'Non assigné',
                'Chauffeur': course.chauffeur.get_full_name() if course.chauffeur else 'Non assigné',
                'Demandeur': demandeur_nom,
                'Origine': course.point_embarquement,
                'Destination': course.destination,
                'Motif': course.motif,
                'Distance': f"{course.distance_parcourue} km" if course.distance_parcourue else 'Non disponible',
                'Statut': dict(Course.STATUS_CHOICES).get(course.statut, course.statut),
                'Date départ': course.date_depart.strftime('%d/%m/%Y %H:%M') if course.date_depart else 'Non disponible',
                'Date fin': course.date_fin.strftime('%d/%m/%Y %H:%M') if course.date_fin else 'Non disponible'
            })
        
        # Générer le rapport au format demandé
        format_export = request.GET.get('format', 'pdf')
        
        if format_export == 'excel':
            return export_to_excel(
                "Rapport des missions", 
                data, 
                "rapport_missions.xlsx"
            )
        else:
            return export_to_pdf(
                "Rapport des missions", 
                data, 
                "rapport_missions.pdf",
                user=request.user
            )
    
    elif type_rapport == 'carburant':
        # Récupérer les données de ravitaillement avec filtres
        queryset = Ravitaillement.objects.all()
        
        # Appliquer les filtres
        vehicule_id = request.GET.get('vehicule')
        station = request.GET.get('station')
        date_debut = request.GET.get('date_debut')
        date_fin = request.GET.get('date_fin')
        montant_min = request.GET.get('montant_min')
        
        if vehicule_id:
            queryset = queryset.filter(vehicule_id=vehicule_id)
        if station:
            queryset = queryset.filter(nom_station__icontains=station)
        if date_debut:
            queryset = queryset.filter(date_ravitaillement__date__gte=date_debut)
        if date_fin:
            queryset = queryset.filter(date_ravitaillement__date__lte=date_fin)
        if montant_min:
            queryset = queryset.filter(cout_total__gte=montant_min)
        
        # Trier par date de ravitaillement (plus récent en premier)
        ravitaillements = queryset.order_by('-date_ravitaillement')
        
        # Calculer les totaux
        total_litres = ravitaillements.aggregate(Sum('litres'))['litres__sum'] or 0
        total_cout = ravitaillements.aggregate(Sum('cout_total'))['cout_total__sum'] or 0
        
        # Préparer les données pour l'exportation
        data = []
        for ravitaillement in ravitaillements:
            data.append({
                'Date': ravitaillement.date_ravitaillement.strftime('%d/%m/%Y %H:%M'),
                'Véhicule': ravitaillement.vehicule.immatriculation,
                'Marque/Modèle': f"{ravitaillement.vehicule.marque} {ravitaillement.vehicule.modele}",
                'Station': ravitaillement.nom_station or 'Non spécifiée',
                'Kilométrage avant': f"{ravitaillement.kilometrage_avant} km",
                'Kilométrage après': f"{ravitaillement.kilometrage_apres} km",
                'Distance': f"{ravitaillement.distance_parcourue} km",
                'Litres': f"{ravitaillement.litres} L",
                'Prix unitaire': f"{ravitaillement.cout_unitaire} $/L",
                'Coût total': f"{ravitaillement.cout_total} $",
                'Consommation': f"{ravitaillement.consommation_moyenne:.2f} L/100km" if ravitaillement.consommation_moyenne > 0 else 'Non disponible',
                'Commentaires': ravitaillement.commentaires or 'Aucun commentaire'
            })
        
        # Ajouter une ligne de total
        data.append({
            'Date': 'TOTAL',
            'Véhicule': '',
            'Marque/Modèle': '',
            'Station': '',
            'Kilométrage avant': '',
            'Kilométrage après': '',
            'Distance': '',
            'Litres': f"{total_litres} L",
            'Prix unitaire': '',
            'Coût total': f"{total_cout} $",
            'Consommation': '',
            'Commentaires': ''
        })
        
        # Générer le rapport au format demandé
        format_export = request.GET.get('format', 'pdf')
        
        if format_export == 'excel':
            return export_to_excel(
                "Rapport de consommation de carburant", 
                data, 
                "rapport_carburant.xlsx"
            )
        else:
            return export_to_pdf(
                "Rapport de consommation de carburant", 
                data, 
                "rapport_carburant.pdf",
                user=request.user
            )
    
    elif type_rapport == 'evaluation_chauffeurs':
        # Récupérer tous les chauffeurs
        chauffeurs = Utilisateur.objects.filter(role='chauffeur')
        
        # Initialiser la liste des données d'évaluation
        evaluations = []
        
        # Appliquer les filtres
        date_debut = request.GET.get('date_debut')
        date_fin = request.GET.get('date_fin')
        chauffeur_id = request.GET.get('chauffeur')
        
        # Filtrer les chauffeurs si nécessaire
        if chauffeur_id:
            chauffeurs = chauffeurs.filter(id=chauffeur_id)
        
        # Pour chaque chauffeur, calculer les statistiques
        for chauffeur in chauffeurs:
            # Initialiser le queryset des courses pour ce chauffeur
            courses_query = Course.objects.filter(chauffeur=chauffeur, statut='terminee')
            
            # Appliquer les filtres de date
            if date_debut:
                courses_query = courses_query.filter(date_fin__date__gte=date_debut)
            if date_fin:
                courses_query = courses_query.filter(date_fin__date__lte=date_fin)
            
            # Calculer les statistiques
            nb_courses = courses_query.count()
            distance_totale = courses_query.aggregate(total=Sum('distance_parcourue'))['total'] or 0
            
            # Calculer la distance moyenne par course
            distance_moyenne = 0
            if nb_courses > 0:
                distance_moyenne = distance_totale / nb_courses
            
            # Ajouter les données d'évaluation à la liste
            evaluations.append({
                'Chauffeur': chauffeur.get_full_name(),
                'Nombre de courses': nb_courses,
                'Distance totale (km)': f"{distance_totale:.2f}",
                'Distance moyenne par course (km)': f"{distance_moyenne:.2f}"
            })
        
        # Trier les évaluations par nombre de courses (décroissant)
        evaluations.sort(key=lambda x: x['Nombre de courses'], reverse=True)
        
        # Générer le rapport au format demandé
        format_export = request.GET.get('format', 'pdf')
        
        if format_export == 'excel':
            return export_to_excel(
                "Rapport d'évaluation des chauffeurs", 
                evaluations, 
                "rapport_evaluation_chauffeurs.xlsx"
            )
        else:
            return export_to_pdf(
                "Rapport d'évaluation des chauffeurs", 
                evaluations, 
                "rapport_evaluation_chauffeurs.pdf",
                user=request.user
            )
    
    elif type_rapport == 'demandeurs':
        # Initialiser le queryset
        queryset = Course.objects.all()
        
        # Appliquer les filtres
        date_debut = request.GET.get('date_debut')
        date_fin = request.GET.get('date_fin')
        
        if date_debut:
            queryset = queryset.filter(date_demande__date__gte=date_debut)
        if date_fin:
            queryset = queryset.filter(date_demande__date__lte=date_fin)
        
        # Agréger les données par demandeur
        demandeurs_stats = (
            queryset.values('demandeur')
            .annotate(
                nombre_courses=Count('id'),
                distance_totale=Sum('distance_parcourue'),
                derniere_demande=Max('date_demande')
            )
            .filter(demandeur__isnull=False)  # Exclure les courses sans demandeur
            .order_by('-nombre_courses')
        )
        
        # Préparer les données pour l'affichage et l'exportation
        data = []
        for stat in demandeurs_stats:
            if stat['demandeur']:
                try:
                    demandeur = Utilisateur.objects.get(id=stat['demandeur'])
                    nom_complet = f"{demandeur.first_name} {demandeur.last_name}"
                    email = demandeur.email
                    departement = demandeur.departement if hasattr(demandeur, 'departement') else 'Non spécifié'
                except Utilisateur.DoesNotExist:
                    nom_complet = "Utilisateur inconnu"
                    email = "Non disponible"
                    departement = "Non disponible"
                
                data.append({
                    'Nom': nom_complet,
                    'Email': email,
                    'Département': departement,
                    'Nombre_de_courses': stat['nombre_courses'],
                    'Distance_totale': f"{stat['distance_totale']:.2f}" if stat['distance_totale'] else '0.00',
                    'Dernière_demande': stat['derniere_demande'].strftime('%d/%m/%Y %H:%M') if stat['derniere_demande'] else 'Non disponible'
                })
        
        # Vérifier si une exportation est demandée
        format_export = request.GET.get('format')
        
        if format_export == 'excel':
            return export_to_excel(
                "Rapport des demandeurs", 
                data, 
                "rapport_demandeurs.xlsx"
            )
        elif format_export == 'pdf':
            return export_to_pdf(
                "Rapport des demandeurs", 
                data, 
                "rapport_demandeurs.pdf",
                user=request.user
            )
        
        # Pagination - 1 demandeur par page (pour test)
        paginator = Paginator(data, 1)
        page = request.GET.get('page')
        
        try:
            demandeurs_pagines = paginator.page(page)
        except PageNotAnInteger:
            # Si la page n'est pas un entier, afficher la première page
            demandeurs_pagines = paginator.page(1)
        except EmptyPage:
            # Si la page est hors limites (par exemple 9999), afficher la dernière page
            demandeurs_pagines = paginator.page(paginator.num_pages)
        
        # Tracer l'action
        ActionTraceur.objects.create(
            utilisateur=request.user,
            action="Consultation du rapport des demandeurs",
        )
        
        context = {
            'demandeurs_stats': demandeurs_pagines,
            'date_debut': date_debut,
            'date_fin': date_fin,
            'title': "Rapport des demandeurs",
        }
        
        return render(request, 'rapport/rapport_demandeurs.html', context)
    
    elif type_rapport == 'vehicules_utilisation':
        # Initialiser le queryset
        queryset = Course.objects.filter(statut='terminee')
        
        # Appliquer les filtres
        date_debut = request.GET.get('date_debut')
        date_fin = request.GET.get('date_fin')
        
        if date_debut:
            queryset = queryset.filter(date_fin__date__gte=date_debut)
        if date_fin:
            queryset = queryset.filter(date_fin__date__lte=date_fin)
        
        # Agréger les données par véhicule
        vehicules_stats_query = (
            queryset.values('vehicule')
            .annotate(
                nombre_courses=Count('id'),
                distance_totale=Sum('distance_parcourue'),
                derniere_utilisation=Max('date_fin')
            )
            .filter(vehicule__isnull=False)  # Exclure les courses sans véhicule assigné
            .order_by('-distance_totale')
        )
        
        # Calculer la distance totale pour tous les véhicules
        total_distance = queryset.aggregate(total=Sum('distance_parcourue'))['total'] or 0
        
        # Enrichir les données avec des informations supplémentaires sur les véhicules
        vehicules_stats_list = []
        for stat in vehicules_stats_query:
            if stat['vehicule']:
                try:
                    vehicule = Vehicule.objects.get(id=stat['vehicule'])
                    
                    # Calculer le kilométrage actuel à partir de la dernière course terminée
                    derniere_course = Course.objects.filter(
                        vehicule=vehicule, 
                        statut='terminee'
                    ).order_by('-date_fin').first()
                    
                    kilometrage_actuel = derniere_course.kilometrage_fin if derniere_course and derniere_course.kilometrage_fin else 'Non disponible'
                    
                    # Calculer la consommation moyenne de carburant
                    ravitaillements = Ravitaillement.objects.filter(vehicule=vehicule)
                    if date_debut:
                        ravitaillements = ravitaillements.filter(date_ravitaillement__date__gte=date_debut)
                    if date_fin:
                        ravitaillements = ravitaillements.filter(date_ravitaillement__date__lte=date_fin)
                    
                    total_litres = ravitaillements.aggregate(Sum('litres'))['litres__sum'] or 0
                    consommation_moyenne = 0
                    if stat['distance_totale'] and stat['distance_totale'] > 0 and total_litres > 0:
                        # Calculer la consommation en L/100km
                        consommation_moyenne = (total_litres * 100) / stat['distance_totale']
                        consommation_moyenne = round(consommation_moyenne, 2)
                    
                    vehicules_stats_list.append({
                        'vehicule_id': stat['vehicule'],
                        'immatriculation': vehicule.immatriculation,
                        'marque': vehicule.marque,
                        'modele': vehicule.modele,
                        'nombre_courses': stat['nombre_courses'],
                        'distance_totale': stat['distance_totale'] or 0,
                        'kilometrage_actuel': kilometrage_actuel,
                        'consommation_moyenne': consommation_moyenne if consommation_moyenne > 0 else 'Non disponible',
                        'derniere_utilisation': stat['derniere_utilisation']
                    })
                except Vehicule.DoesNotExist:
                    vehicules_stats_list.append({
                        'vehicule_id': stat['vehicule'],
                        'immatriculation': "Inconnu",
                        'marque': "Inconnu",
                        'modele': "Inconnu",
                        'nombre_courses': stat['nombre_courses'],
                        'distance_totale': stat['distance_totale'] or 0,
                        'kilometrage_actuel': 'Non disponible',
                        'consommation_moyenne': 'Non disponible',
                        'derniere_utilisation': stat['derniere_utilisation']
                    })
        
        # Vérifier si une exportation est demandée
        format_export = request.GET.get('format')
        
        if format_export == 'excel' or format_export == 'pdf':
            # Préparer les données pour l'exportation
            data = []
            for item in vehicules_stats_list:
                data.append({
                    'Immatriculation': item['immatriculation'],
                    'Marque/Modèle': f"{item['marque']} {item['modele']}",
                    'Nombre de courses': item['nombre_courses'],
                    'Distance totale (km)': f"{item['distance_totale']:.2f}",
                    'Kilométrage actuel': item['kilometrage_actuel'],
                    'Consommation moyenne (L/100km)': item['consommation_moyenne'],
                    'Dernière utilisation': item['derniere_utilisation'].strftime('%d/%m/%Y %H:%M') if item['derniere_utilisation'] else 'Non disponible'
                })
            
            # Ajouter une ligne de total
            data.append({
                'Immatriculation': 'TOTAL',
                'Marque/Modèle': '',
                'Nombre de courses': sum(item['nombre_courses'] for item in vehicules_stats_list),
                'Distance totale (km)': f"{total_distance:.2f}",
                'Kilométrage actuel': '',
                'Consommation moyenne (L/100km)': '',
                'Dernière utilisation': ''
            })
            
            if format_export == 'excel':
                return export_to_excel(
                    "Rapport d'utilisation des véhicules", 
                    data, 
                    "rapport_vehicules_utilisation.xlsx"
                )
            else:
                return export_to_pdf(
                    "Rapport d'utilisation des véhicules", 
                    data, 
                    "rapport_vehicules_utilisation.pdf",
                    user=request.user
                )
        
        # Pagination - 2 véhicules par page (pour test)
        paginator = Paginator(vehicules_stats_list, 2)
        page = request.GET.get('page')
        
        try:
            vehicules_stats = paginator.page(page)
        except PageNotAnInteger:
            # Si la page n'est pas un entier, afficher la première page
            vehicules_stats = paginator.page(1)
        except EmptyPage:
            # Si la page est hors limites (par exemple 9999), afficher la dernière page
            vehicules_stats = paginator.page(paginator.num_pages)
        
        # Tracer l'action
        ActionTraceur.objects.create(
            utilisateur=request.user,
            action="Consultation du rapport d'utilisation des véhicules",
        )
        
        context = {
            'vehicules_stats': vehicules_stats,
            'total_distance': total_distance,
            'date_debut': date_debut,
            'date_fin': date_fin,
            'title': "Rapport d'utilisation des véhicules",
        }
        
        return render(request, 'rapport/rapport_vehicules_utilisation.html', context)
    
    elif type_rapport == 'depenses_carburant_entretien':
        # Initialiser les queryset
        queryset_ravitaillements = Ravitaillement.objects.all()
        queryset_entretiens = Entretien.objects.all()
        
        # Appliquer les filtres
        vehicule_id = request.GET.get('vehicule')
        date_debut = request.GET.get('date_debut')
        date_fin = request.GET.get('date_fin')
        
        # Filtrer par véhicule si spécifié
        if vehicule_id:
            queryset_ravitaillements = queryset_ravitaillements.filter(vehicule_id=vehicule_id)
            queryset_entretiens = queryset_entretiens.filter(vehicule_id=vehicule_id)
        
        # Filtrer par date de début si spécifiée
        if date_debut:
            queryset_ravitaillements = queryset_ravitaillements.filter(date_ravitaillement__date__gte=date_debut)
            queryset_entretiens = queryset_entretiens.filter(date_creation__date__gte=date_debut)
        
        # Filtrer par date de fin si spécifiée
        if date_fin:
            queryset_ravitaillements = queryset_ravitaillements.filter(date_ravitaillement__date__lte=date_fin)
            queryset_entretiens = queryset_entretiens.filter(date_creation__date__lte=date_fin)
        
        # Calculer les totaux par véhicule
        vehicules = Vehicule.objects.all()
        depenses_par_vehicule = []
        
        for vehicule in vehicules:
            # Calculer les dépenses de carburant
            ravitaillements_vehicule = queryset_ravitaillements.filter(vehicule=vehicule)
            cout_carburant = ravitaillements_vehicule.aggregate(Sum('cout_total'))['cout_total__sum'] or 0
            
            # Calculer les dépenses d'entretien
            entretiens_vehicule = queryset_entretiens.filter(vehicule=vehicule)
            cout_entretien = entretiens_vehicule.aggregate(Sum('cout'))['cout__sum'] or 0
            
            # Ajouter les données au tableau si le véhicule a des dépenses
            if cout_carburant > 0 or cout_entretien > 0:
                depenses_par_vehicule.append({
                    'vehicule': vehicule,
                    'immatriculation': vehicule.immatriculation,
                    'marque_modele': f"{vehicule.marque} {vehicule.modele}",
                    'cout_carburant': cout_carburant,
                    'cout_entretien': cout_entretien,
                    'cout_total': cout_carburant + cout_entretien
                })
        
        # Trier par coût total décroissant
        depenses_par_vehicule.sort(key=lambda x: x['cout_total'], reverse=True)
        
        # Calculer les totaux généraux
        total_carburant = sum(item['cout_carburant'] for item in depenses_par_vehicule)
        total_entretien = sum(item['cout_entretien'] for item in depenses_par_vehicule)
        total_general = total_carburant + total_entretien
        
        # Préparer les données pour l'exportation
        data = []
        for item in depenses_par_vehicule:
            data.append({
                'Immatriculation': item['immatriculation'],
                'Marque/Modèle': item['marque_modele'],
                'Dépenses carburant ($)': f"{item['cout_carburant']:.2f}",
                'Dépenses entretien ($)': f"{item['cout_entretien']:.2f}",
                'Coût total ($)': f"{item['cout_total']:.2f}",
            })
        
        # Ajouter une ligne de total
        data.append({
            'Immatriculation': 'TOTAL',
            'Marque/Modèle': '',
            'Dépenses carburant ($)': f"{total_carburant:.2f}",
            'Dépenses entretien ($)': f"{total_entretien:.2f}",
            'Coût total ($)': f"{total_general:.2f}",
        })
        
        # Générer le rapport au format demandé
        format_export = request.GET.get('format', 'pdf')
        
        if format_export == 'excel':
            return export_to_excel(
                "Rapport de dépenses carburant et entretien", 
                data, 
                "rapport_depenses_carburant_entretien.xlsx"
            )
        else:
            return export_to_pdf(
                "Rapport de dépenses carburant et entretien", 
                data, 
                "rapport_depenses_carburant_entretien.pdf",
                user=request.user
            )
    
    # Si on arrive ici, c'est qu'aucun rapport n'a été généré
    messages.warning(request, f"Aucun rapport n'a été généré pour le type {type_rapport}.")
    return redirect('rapport:dashboard')

@login_required
@user_passes_test(is_admin_or_superuser)
def rapport_evaluation_chauffeurs(request):
    """Vue pour générer des rapports d'évaluation des chauffeurs"""
    # Récupérer tous les chauffeurs
    chauffeurs = Utilisateur.objects.filter(role='chauffeur')
    
    # Initialiser la liste des données d'évaluation
    evaluations = []
    
    # Appliquer les filtres
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    chauffeur_id = request.GET.get('chauffeur')
    
    # Filtrer les chauffeurs si nécessaire
    if chauffeur_id:
        chauffeurs = chauffeurs.filter(id=chauffeur_id)
    
    # Pour chaque chauffeur, calculer les statistiques
    for chauffeur in chauffeurs:
        # Initialiser le queryset des courses pour ce chauffeur
        courses_query = Course.objects.filter(chauffeur=chauffeur, statut='terminee')
        
        # Appliquer les filtres de date
        if date_debut:
            courses_query = courses_query.filter(date_fin__date__gte=date_debut)
        if date_fin:
            courses_query = courses_query.filter(date_fin__date__lte=date_fin)
        
        # Calculer les statistiques
        nb_courses = courses_query.count()
        distance_totale = courses_query.aggregate(total=Sum('distance_parcourue'))['total'] or 0
        
        # Calculer la distance moyenne par course
        distance_moyenne = 0
        if nb_courses > 0:
            distance_moyenne = distance_totale / nb_courses
        
        # Ajouter les données d'évaluation à la liste
        evaluations.append({
            'chauffeur': chauffeur,
            'nb_courses': nb_courses,
            'distance_totale': distance_totale,
            'distance_moyenne': distance_moyenne,
        })
    
    # Trier les évaluations par nombre de courses (décroissant)
    evaluations.sort(key=lambda x: x['nb_courses'], reverse=True)
    
    # Tracer l'action
    ActionTraceur.objects.create(
        utilisateur=request.user,
        action="Consultation du rapport d'évaluation des chauffeurs",
    )
    
    context = {
        'evaluations': evaluations,
        'chauffeurs': chauffeurs,
        'date_debut': date_debut,
        'date_fin': date_fin,
        'selected_chauffeur': chauffeur_id,
        'title': "Rapport d'évaluation des chauffeurs",
    }
    
    return render(request, 'rapport/rapport_evaluation_chauffeurs.html', context)

@login_required
@user_passes_test(is_admin_or_superuser)
def rapport_demandeurs(request):
    """Vue pour générer des rapports sur les demandeurs de courses"""
    # Initialiser le queryset
    queryset = Course.objects.all()
    
    # Appliquer les filtres
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    
    if date_debut:
        queryset = queryset.filter(date_demande__date__gte=date_debut)
    if date_fin:
        queryset = queryset.filter(date_demande__date__lte=date_fin)
    
    # Agréger les données par demandeur
    demandeurs_stats = (
        queryset.values('demandeur')
        .annotate(
            nombre_courses=Count('id'),
            distance_totale=Sum('distance_parcourue'),
            derniere_demande=Max('date_demande')
        )
        .filter(demandeur__isnull=False)  # Exclure les courses sans demandeur
        .order_by('-nombre_courses')
    )
    
    # Préparer les données pour l'affichage et l'exportation
    data = []
    for stat in demandeurs_stats:
        if stat['demandeur']:
            try:
                demandeur = Utilisateur.objects.get(id=stat['demandeur'])
                nom_complet = f"{demandeur.first_name} {demandeur.last_name}"
                email = demandeur.email
                departement = demandeur.departement if hasattr(demandeur, 'departement') else 'Non spécifié'
            except Utilisateur.DoesNotExist:
                nom_complet = "Utilisateur inconnu"
                email = "Non disponible"
                departement = "Non disponible"
            
            data.append({
                'Nom': nom_complet,
                'Email': email,
                'Département': departement,
                'Nombre_de_courses': stat['nombre_courses'],
                'Distance_totale': f"{stat['distance_totale']:.2f}" if stat['distance_totale'] else '0.00',
                'Dernière_demande': stat['derniere_demande'].strftime('%d/%m/%Y %H:%M') if stat['derniere_demande'] else 'Non disponible'
            })
    
    # Vérifier si une exportation est demandée
    format_export = request.GET.get('format')
    
    if format_export == 'excel':
        return export_to_excel(
            "Rapport des demandeurs", 
            data, 
            "rapport_demandeurs.xlsx"
        )
    elif format_export == 'pdf':
        return export_to_pdf(
            "Rapport des demandeurs", 
            data, 
            "rapport_demandeurs.pdf",
            user=request.user
        )
    
    # Pagination - 1 demandeur par page (pour test)
    paginator = Paginator(data, 1)
    page = request.GET.get('page')
    
    try:
        demandeurs_pagines = paginator.page(page)
    except PageNotAnInteger:
        # Si la page n'est pas un entier, afficher la première page
        demandeurs_pagines = paginator.page(1)
    except EmptyPage:
        # Si la page est hors limites (par exemple 9999), afficher la dernière page
        demandeurs_pagines = paginator.page(paginator.num_pages)
    
    # Tracer l'action
    ActionTraceur.objects.create(
        utilisateur=request.user,
        action="Consultation du rapport des demandeurs",
    )
    
    context = {
        'demandeurs_stats': demandeurs_pagines,
        'date_debut': date_debut,
        'date_fin': date_fin,
        'title': "Rapport des demandeurs",
    }
    
    return render(request, 'rapport/rapport_demandeurs.html', context)

@login_required
@user_passes_test(is_admin_or_superuser)
def rapport_depenses_carburant_entretien(request):
    """Vue pour générer des rapports sur les dépenses de carburant et d'entretien"""
    # Initialiser les queryset
    queryset_ravitaillements = Ravitaillement.objects.all()
    queryset_entretiens = Entretien.objects.all()
    
    # Appliquer les filtres
    vehicule_id = request.GET.get('vehicule')
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    
    # Filtrer par véhicule si spécifié
    if vehicule_id:
        queryset_ravitaillements = queryset_ravitaillements.filter(vehicule_id=vehicule_id)
        queryset_entretiens = queryset_entretiens.filter(vehicule_id=vehicule_id)
    
    # Filtrer par date de début si spécifiée
    if date_debut:
        queryset_ravitaillements = queryset_ravitaillements.filter(date_ravitaillement__date__gte=date_debut)
        queryset_entretiens = queryset_entretiens.filter(date_creation__date__gte=date_debut)
    
    # Filtrer par date de fin si spécifiée
    if date_fin:
        queryset_ravitaillements = queryset_ravitaillements.filter(date_ravitaillement__date__lte=date_fin)
        queryset_entretiens = queryset_entretiens.filter(date_creation__date__lte=date_fin)
    
    # Calculer les totaux par véhicule
    vehicules = Vehicule.objects.all()
    depenses_par_vehicule = []
    
    for vehicule in vehicules:
        # Calculer les dépenses de carburant
        ravitaillements_vehicule = queryset_ravitaillements.filter(vehicule=vehicule)
        cout_carburant = ravitaillements_vehicule.aggregate(Sum('cout_total'))['cout_total__sum'] or 0
        
        # Calculer les dépenses d'entretien
        entretiens_vehicule = queryset_entretiens.filter(vehicule=vehicule)
        cout_entretien = entretiens_vehicule.aggregate(Sum('cout'))['cout__sum'] or 0
        
        # Ajouter les données au tableau si le véhicule a des dépenses
        if cout_carburant > 0 or cout_entretien > 0:
            depenses_par_vehicule.append({
                'vehicule': vehicule,
                'immatriculation': vehicule.immatriculation,
                'marque_modele': f"{vehicule.marque} {vehicule.modele}",
                'cout_carburant': cout_carburant,
                'cout_entretien': cout_entretien,
                'cout_total': cout_carburant + cout_entretien
            })
    
    # Trier par coût total décroissant
    depenses_par_vehicule.sort(key=lambda x: x['cout_total'], reverse=True)
    
    # Calculer les totaux généraux
    total_carburant = sum(item['cout_carburant'] for item in depenses_par_vehicule)
    total_entretien = sum(item['cout_entretien'] for item in depenses_par_vehicule)
    total_general = total_carburant + total_entretien
    
    # Vérifier si une exportation est demandée
    format_export = request.GET.get('format')
    
    if format_export == 'excel' or format_export == 'pdf':
        # Préparer les données pour l'exportation
        data = []
        for item in depenses_par_vehicule:
            data.append({
                'Immatriculation': item['immatriculation'],
                'Marque/Modèle': item['marque_modele'],
                'Dépenses carburant ($)': f"{item['cout_carburant']:.2f}",
                'Dépenses entretien ($)': f"{item['cout_entretien']:.2f}",
                'Coût total ($)': f"{item['cout_total']:.2f}",
            })
        
        # Ajouter une ligne de total
        data.append({
            'Immatriculation': 'TOTAL',
            'Marque/Modèle': '',
            'Dépenses carburant ($)': f"{total_carburant:.2f}",
            'Dépenses entretien ($)': f"{total_entretien:.2f}",
            'Coût total ($)': f"{total_general:.2f}",
        })
        
        if format_export == 'excel':
            return export_to_excel(
                "Rapport de dépenses carburant et entretien", 
                data, 
                "rapport_depenses_carburant_entretien.xlsx"
            )
        else:
            return export_to_pdf(
                "Rapport de dépenses carburant et entretien", 
                data, 
                "rapport_depenses_carburant_entretien.pdf",
                user=request.user
            )
    
    # Récupérer tous les véhicules pour le filtre
    vehicules = Vehicule.objects.all().order_by('immatriculation')
    
    # Tracer l'action
    ActionTraceur.objects.create(
        utilisateur=request.user,
        action="Consultation du rapport de dépenses carburant et entretien",
    )
    
    context = {
        'depenses_par_vehicule': depenses_par_vehicule,
        'total_carburant': total_carburant,
        'total_entretien': total_entretien,
        'total_general': total_general,
        'vehicules': vehicules,
        'date_debut': date_debut,
        'date_fin': date_fin,
        'selected_vehicule': vehicule_id,
        'title': "Rapport de dépenses carburant et entretien",
    }
    
    return render(request, 'rapport/rapport_depenses_carburant_entretien.html', context)
