from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.forms import SetPasswordForm
from django.utils import timezone
from django.http import HttpResponse
import os
from .models import Vehicule, Course, ActionTraceur, Utilisateur
from .forms import UtilisateurCreationForm, UtilisateurChangeForm
from .vehicule_forms import VehiculeForm
from .utils import render_to_pdf
from entretien.models import Entretien
from ravitaillement.models import Ravitaillement
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

def home_view(request):
    """Vue pour la page d'accueil"""
    context = {}
    
    if request.user.is_authenticated:
        # Récupérer les statistiques
        context['vehicules_count'] = Vehicule.objects.count()
        context['courses_count'] = Course.objects.count()
        context['entretiens_count'] = Entretien.objects.count()
        context['ravitaillements_count'] = Ravitaillement.objects.count()
        
        # Récupérer les activités récentes
        context['activites'] = ActionTraceur.objects.all().order_by('-date_action')[:10]
    
    return render(request, 'core/home.html', context)

def login_view(request):
    """Vue pour la page de connexion"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenue, {user.username} !')
            
            # Rediriger vers la page appropriée en fonction du rôle
            if user.role == 'securite':
                return redirect('securite:dashboard')
            elif user.role == 'demandeur':
                return redirect('demandeur:dashboard')
            elif user.role == 'dispatch':
                return redirect('dispatch:dashboard')
            elif user.role == 'chauffeur':
                return redirect('chauffeur:dashboard')
            else:
                return redirect('home')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    
    return render(request, 'core/login.html')

def logout_view(request):
    """Vue pour la déconnexion"""
    logout(request)
    messages.info(request, 'Vous avez été déconnecté avec succès.')
    return redirect('login')

@login_required
def profile_view(request):
    """Vue pour la page de profil utilisateur"""
    return render(request, 'core/profile.html')

# Fonction pour vérifier si l'utilisateur est administrateur
def is_admin(user):
    # Vérification stricte : l'utilisateur doit être authentifié et avoir le rôle 'admin'
    # Les superutilisateurs ne sont pas automatiquement considérés comme administrateurs
    return user.is_authenticated and user.role == 'admin'

@login_required
@user_passes_test(is_admin)
def user_list(request):
    """Vue pour afficher la liste des utilisateurs (réservée aux administrateurs)"""
    users_list = Utilisateur.objects.all().order_by('username')
    
    # Pagination - 5 utilisateurs par page (réduit de 10 à 5)
    paginator = Paginator(users_list, 5)
    page = request.GET.get('page')
    
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        # Si la page n'est pas un entier, afficher la première page
        users = paginator.page(1)
    except EmptyPage:
        # Si la page est hors limites (par exemple 9999), afficher la dernière page
        users = paginator.page(paginator.num_pages)
    
    # Tracer l'action
    ActionTraceur.objects.create(
        utilisateur=request.user,
        action="Consultation de la liste des utilisateurs",
    )
    
    return render(request, 'core/user_list.html', {'users': users})

@login_required
@user_passes_test(is_admin)
def user_create(request):
    """Vue pour créer un nouvel utilisateur (réservée aux administrateurs)"""
    if request.method == 'POST':
        form = UtilisateurCreationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                user = form.save()
                
                # Tracer l'action
                ActionTraceur.objects.create(
                    utilisateur=request.user,
                    action=f"Création de l'utilisateur {user.username}",
                    details=f"Rôle: {user.get_role_display()}"
                )
                
                messages.success(request, f"L'utilisateur {user.username} a été créé avec succès.")
                return redirect('user_list')
            except Exception as e:
                messages.error(request, f"Erreur lors de la création de l'utilisateur: {str(e)}")
        else:
            # Afficher les erreurs du formulaire
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erreur dans le champ {field}: {error}")
    else:
        form = UtilisateurCreationForm()
    
    # Afficher les champs disponibles dans le formulaire pour le débogage
    print(f"Champs disponibles dans le formulaire: {list(form.fields.keys())}")
    
    return render(request, 'core/user_form.html', {'form': form, 'title': 'Créer un utilisateur', 'mode': 'create'})

@login_required
@user_passes_test(is_admin)
def user_edit(request, pk):
    """Vue pour modifier un utilisateur existant (réservée aux administrateurs)"""
    user_to_edit = get_object_or_404(Utilisateur, pk=pk)
    
    if request.method == 'POST':
        form = UtilisateurChangeForm(request.POST, request.FILES, instance=user_to_edit)
        if form.is_valid():
            try:
                form.save()
                
                # Tracer l'action
                ActionTraceur.objects.create(
                    utilisateur=request.user,
                    action=f"Modification de l'utilisateur {user_to_edit.username}",
                    details=f"Rôle: {user_to_edit.get_role_display()}"
                )
                
                messages.success(request, f"L'utilisateur {user_to_edit.username} a été modifié avec succès.")
                return redirect('user_list')
            except Exception as e:
                messages.error(request, f"Erreur lors de la modification de l'utilisateur: {str(e)}")
        else:
            # Afficher les erreurs du formulaire
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erreur dans le champ {field}: {error}")
    else:
        form = UtilisateurChangeForm(instance=user_to_edit)
    
    return render(request, 'core/user_form.html', {'form': form, 'title': 'Modifier un utilisateur', 'user_to_edit': user_to_edit, 'mode': 'edit'})

@login_required
@user_passes_test(is_admin)
def user_password_reset(request, pk):
    """Vue pour réinitialiser le mot de passe d'un utilisateur (réservée aux administrateurs)"""
    user = get_object_or_404(Utilisateur, pk=pk)
    
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            
            # Tracer l'action
            ActionTraceur.objects.create(
                utilisateur=request.user,
                action=f"Réinitialisation du mot de passe de l'utilisateur {user.username}",
            )
            
            messages.success(request, f"Le mot de passe de l'utilisateur {user.username} a été réinitialisé avec succès.")
            return redirect('user_list')
    else:
        form = SetPasswordForm(user)
    
    return render(request, 'core/user_password_reset.html', {'form': form, 'user': user})

@login_required
@user_passes_test(is_admin)
def user_toggle_active(request, pk):
    """Vue pour activer/désactiver un utilisateur (réservée aux administrateurs)"""
    user = get_object_or_404(Utilisateur, pk=pk)
    
    # Ne pas permettre de désactiver son propre compte
    if user == request.user:
        messages.error(request, "Vous ne pouvez pas désactiver votre propre compte.")
        return redirect('user_list')
    
    user.is_active = not user.is_active
    user.save()
    
    action = "Activation" if user.is_active else "Désactivation"
    
    # Tracer l'action
    ActionTraceur.objects.create(
        utilisateur=request.user,
        action=f"{action} de l'utilisateur {user.username}",
    )
    
    messages.success(request, f"L'utilisateur {user.username} a été {'activé' if user.is_active else 'désactivé'} avec succès.")
    return redirect('user_list')


# Gestion des véhicules
@login_required
@user_passes_test(is_admin)
def vehicule_list(request):
    """Vue pour afficher la liste des véhicules (réservée aux administrateurs)"""
    vehicules_list = Vehicule.objects.all().order_by('immatriculation')
    
    # Pagination - 5 véhicules par page
    paginator = Paginator(vehicules_list, 5)
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
        action="Consultation de la liste des véhicules",
    )
    
    return render(request, 'core/vehicule_list.html', {'vehicules': vehicules})

@login_required
@user_passes_test(is_admin)
def vehicule_create(request):
    """Vue pour créer un nouveau véhicule (réservée aux administrateurs)"""
    if request.method == 'POST':
        form = VehiculeForm(request.POST, request.FILES, createur=request.user)
        if form.is_valid():
            try:
                vehicule = form.save()
                
                # Tracer l'action
                ActionTraceur.objects.create(
                    utilisateur=request.user,
                    action=f"Création du véhicule {vehicule.immatriculation}",
                    details=f"Marque: {vehicule.marque}, Modèle: {vehicule.modele}"
                )
                
                messages.success(request, f"Le véhicule {vehicule.immatriculation} a été créé avec succès.")
                return redirect('vehicule_list')
            except Exception as e:
                messages.error(request, f"Erreur lors de la création du véhicule: {str(e)}")
        else:
            # Afficher les erreurs du formulaire
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erreur dans le champ {field}: {error}")
    else:
        form = VehiculeForm(createur=request.user)
    
    return render(request, 'core/vehicule_form.html', {'form': form, 'title': 'Ajouter un véhicule', 'mode': 'create'})

@login_required
@user_passes_test(is_admin)
def vehicule_edit(request, pk):
    """Vue pour modifier un véhicule existant (réservée aux administrateurs)"""
    vehicule = get_object_or_404(Vehicule, pk=pk)
    
    if request.method == 'POST':
        form = VehiculeForm(request.POST, request.FILES, instance=vehicule, createur=request.user)
        if form.is_valid():
            try:
                form.save()
                
                # Tracer l'action
                ActionTraceur.objects.create(
                    utilisateur=request.user,
                    action=f"Modification du véhicule {vehicule.immatriculation}",
                    details=f"Marque: {vehicule.marque}, Modèle: {vehicule.modele}"
                )
                
                messages.success(request, f"Le véhicule {vehicule.immatriculation} a été modifié avec succès.")
                return redirect('vehicule_list')
            except Exception as e:
                messages.error(request, f"Erreur lors de la modification du véhicule: {str(e)}")
        else:
            # Afficher les erreurs du formulaire
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erreur dans le champ {field}: {error}")
    else:
        form = VehiculeForm(instance=vehicule, createur=request.user)
    
    return render(request, 'core/vehicule_form.html', {'form': form, 'title': 'Modifier un véhicule', 'vehicule': vehicule, 'mode': 'edit'})

@login_required
@user_passes_test(is_admin)
def vehicule_delete(request, pk):
    """Vue pour supprimer un véhicule (réservée aux administrateurs)"""
    vehicule = get_object_or_404(Vehicule, pk=pk)
    
    if request.method == 'POST':
        # Enregistrer l'action
        ActionTraceur.objects.create(
            utilisateur=request.user,
            action=f"Suppression du véhicule {vehicule.immatriculation}",
            details="Module: Véhicules"
        )
        
        # Supprimer le véhicule
        vehicule.delete()
        
        messages.success(request, f"Le véhicule {vehicule.immatriculation} a été supprimé avec succès.")
        return redirect('vehicule_list')
    
    context = {
        'vehicule': vehicule
    }
    
    return render(request, 'core/vehicule_confirm_delete.html', context)

# Vue pour afficher les détails d'un véhicule
@login_required
@user_passes_test(is_admin)
def vehicule_detail(request, pk):
    """Vue pour afficher les détails d'un véhicule (réservée aux administrateurs)"""
    vehicule = get_object_or_404(Vehicule, pk=pk)
    
    # Enregistrer l'action
    ActionTraceur.objects.create(
        utilisateur=request.user,
        action=f"Consultation des détails du véhicule {vehicule.immatriculation}",
        details="Module: Véhicules"
    )
    
    context = {
        'vehicule': vehicule
    }
    
    return render(request, 'core/vehicule_detail.html', context)

@login_required
@user_passes_test(is_admin)
def vehicule_detail_pdf(request, pk):
    """Vue pour générer un PDF des détails d'un véhicule (réservée aux administrateurs)"""
    vehicule = get_object_or_404(Vehicule, pk=pk)
    
    # Enregistrer l'action
    ActionTraceur.objects.create(
        utilisateur=request.user,
        action=f"Exportation PDF des détails du véhicule {vehicule.immatriculation}",
        details="Module: Véhicules"
    )
    
    # Chemin absolu du logo MAMO
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logo_path = os.path.abspath(os.path.join(base_dir, 'static', 'img', 'logo_mamo.png'))
    
    # Préparer les données du véhicule avec le chemin absolu de l'image si elle existe
    vehicule_data = {
        'immatriculation': vehicule.immatriculation,
        'marque': vehicule.marque,
        'modele': vehicule.modele,
        'couleur': vehicule.couleur,
        'numero_chassis': vehicule.numero_chassis,
        'date_creation': vehicule.date_creation,
        'date_modification': vehicule.date_modification,
        'date_expiration_assurance': vehicule.date_expiration_assurance,
        'date_expiration_controle_technique': vehicule.date_expiration_controle_technique,
        'date_expiration_vignette': vehicule.date_expiration_vignette,
        'date_expiration_stationnement': vehicule.date_expiration_stationnement,
        'jours_avant_expiration_assurance': vehicule.jours_avant_expiration_assurance(),
        'jours_avant_expiration_controle': vehicule.jours_avant_expiration_controle(),
        'jours_avant_expiration_vignette': vehicule.jours_avant_expiration_vignette(),
        'image_url': None
    }
    
    # Créer une image de véhicule avec les informations du véhicule
    import base64
    from PIL import Image, ImageDraw, ImageFont
    import io
    
    # Vérifier si le véhicule a une image
    vehicle_image_base64 = None
    if vehicule.image and hasattr(vehicule.image, 'path') and os.path.exists(vehicule.image.path):
        try:
            # Ouvrir l'image du véhicule avec PIL
            with open(vehicule.image.path, 'rb') as img_file:
                img_data = img_file.read()
                vehicle_image_base64 = base64.b64encode(img_data).decode('utf-8')
        except Exception as e:
            print(f"Erreur lors de l'accès à l'image du véhicule: {e}")
    
    # Si le véhicule n'a pas d'image ou si l'accès à l'image a échoué, créer une image de remplacement
    if not vehicle_image_base64:
        # Créer une image avec un fond blanc
        width, height = 300, 200
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Dessiner un cadre
        draw.rectangle([(0, 0), (width-1, height-1)], outline='#2c3e50')
        
        # Ajouter un en-tête coloré
        draw.rectangle([(0, 0), (width, 40)], fill='#2c3e50')
        
        # Essayer de charger une police
        try:
            font_large = ImageFont.truetype("arial.ttf", 24)
            font_medium = ImageFont.truetype("arial.ttf", 18)
            font_small = ImageFont.truetype("arial.ttf", 14)
        except IOError:
            # Si la police n'est pas disponible, utiliser la police par défaut
            font_large = ImageFont.load_default()
            font_medium = font_large
            font_small = font_large
        
        # Ajouter l'immatriculation en blanc dans l'en-tête
        draw.text((10, 10), vehicule.immatriculation, fill='white', font=font_large)
        
        # Ajouter les informations du véhicule
        draw.text((10, 50), f"Marque: {vehicule.marque}", fill='black', font=font_medium)
        draw.text((10, 80), f"Modèle: {vehicule.modele}", fill='black', font=font_medium)
        draw.text((10, 110), f"Couleur: {vehicule.couleur}", fill='black', font=font_medium)
        draw.text((10, 140), f"Châssis: {vehicule.numero_chassis[:10]}...", fill='black', font=font_small)
        
        # Convertir l'image en base64
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        img_data = buffer.read()
        vehicle_image_base64 = base64.b64encode(img_data).decode('utf-8')
    
    # Ajouter l'image en base64 aux données du véhicule
    vehicule_data['image_base64'] = vehicle_image_base64
    
    context = {
        'vehicule': vehicule_data,
        'date_generation': timezone.now().strftime('%d/%m/%Y %H:%M'),
        'logo_path': logo_path,
        'has_image': vehicule.image is not None and hasattr(vehicule.image, 'url')
    }
    
    # Générer le PDF
    pdf = render_to_pdf('core/pdf/vehicule_detail_pdf.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"vehicule_{vehicule.immatriculation}_{timezone.now().strftime('%Y%m%d')}.pdf"
        content = f"attachment; filename={filename}"
        response['Content-Disposition'] = content
        return response
    
    return HttpResponse("Une erreur s'est produite lors de la génération du PDF.")

@login_required
@user_passes_test(is_admin)
def vehicule_list_pdf(request):
    """Vue pour générer un PDF de la liste des véhicules (réservée aux administrateurs)"""
    vehicules = Vehicule.objects.all().order_by('immatriculation')
    
    # Filtrage si demandé
    marque = request.GET.get('marque', '')
    if marque:
        vehicules = vehicules.filter(marque__icontains=marque)
    
    modele = request.GET.get('modele', '')
    if modele:
        vehicules = vehicules.filter(modele__icontains=modele)
    
    immatriculation = request.GET.get('immatriculation', '')
    if immatriculation:
        vehicules = vehicules.filter(immatriculation__icontains=immatriculation)
    
    # Enregistrer l'action
    ActionTraceur.objects.create(
        utilisateur=request.user,
        action="Exportation PDF de la liste des véhicules",
        details=f"Module: Véhicules, Filtres: {marque} {modele} {immatriculation}"
    )
    
    # Chemin du logo MAMO (à adapter selon l'emplacement réel du logo)
    logo_path = os.path.join('static', 'img', 'logo_mamo.png')
    
    context = {
        'vehicules': vehicules,
        'date_generation': timezone.now().strftime('%d/%m/%Y %H:%M'),
        'logo_path': logo_path
    }
    
    # Générer le PDF
    pdf = render_to_pdf('core/pdf/vehicule_list_pdf.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"liste_vehicules_{timezone.now().strftime('%Y%m%d')}.pdf"
        content = f"attachment; filename={filename}"
        response['Content-Disposition'] = content
        return response
    
    return HttpResponse("Une erreur s'est produite lors de la génération du PDF.")
