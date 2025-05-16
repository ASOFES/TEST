from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Utilisateur(AbstractUser):
    """Modèle utilisateur personnalisé avec des rôles spécifiques"""
    ROLE_CHOICES = (
        ('admin', 'Administrateur'),
        ('chauffeur', 'Chauffeur'),
        ('securite', 'Sécurité'),
        ('demandeur', 'Demandeur de missions'),
        ('dispatch', 'Dispatcher'),
        ('consultant', 'Consultant'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='demandeur')
    telephone = models.CharField(max_length=20, blank=True, null=True)
    adresse = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to='photos_profil/', blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.get_role_display()})"

class Vehicule(models.Model):
    """Modèle pour les véhicules"""
    immatriculation = models.CharField(max_length=20, unique=True)
    marque = models.CharField(max_length=50)
    modele = models.CharField(max_length=50)
    couleur = models.CharField(max_length=30)
    numero_chassis = models.CharField(max_length=50, unique=True)
    image = models.ImageField(upload_to='images_vehicules/', blank=True, null=True)
    date_immatriculation = models.DateField(null=True, blank=True)
    date_expiration_assurance = models.DateField()
    date_expiration_controle_technique = models.DateField()
    date_expiration_vignette = models.DateField()
    date_expiration_stationnement = models.DateField()
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    createur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, related_name='vehicules_crees')
    
    def __str__(self):
        return f"{self.immatriculation} - {self.marque} {self.modele}"
    
    def jours_avant_expiration_assurance(self):
        """Retourne le nombre de jours avant l'expiration de l'assurance"""
        return (self.date_expiration_assurance - timezone.now().date()).days
    
    def jours_avant_expiration_controle(self):
        """Retourne le nombre de jours avant l'expiration du contrôle technique"""
        return (self.date_expiration_controle_technique - timezone.now().date()).days
    
    def jours_avant_expiration_vignette(self):
        """Retourne le nombre de jours avant l'expiration de la vignette"""
        return (self.date_expiration_vignette - timezone.now().date()).days
        
    def est_disponible(self):
        """Vérifie si le véhicule est disponible (non assigné à une course en cours)"""
        # Import à l'intérieur de la méthode pour éviter les imports circulaires
        # Course est déjà défini dans ce même fichier, donc pas besoin d'import
        return not self.course_set.filter(
            statut__in=['validee', 'en_cours']
        ).exists()

class Course(models.Model):
    """Modèle pour les courses/missions"""
    STATUS_CHOICES = (
        ('en_attente', 'En attente'),
        ('validee', 'Validée'),
        ('refusee', 'Refusée'),
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée'),
        ('annulee', 'Annulée'),
    )
    
    demandeur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='courses_demandees')
    point_embarquement = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    motif = models.TextField()
    date_demande = models.DateTimeField(auto_now_add=True)
    date_souhaitee = models.DateTimeField(null=True, blank=True)
    
    # Champs remplis par le dispatcher
    chauffeur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses_assignees')
    vehicule = models.ForeignKey(Vehicule, on_delete=models.SET_NULL, null=True, blank=True)
    dispatcher = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses_dispatched')
    date_validation = models.DateTimeField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_attente')
    
    # Champs remplis par le chauffeur
    kilometrage_depart = models.PositiveIntegerField(null=True, blank=True)
    kilometrage_fin = models.PositiveIntegerField(null=True, blank=True)
    date_depart = models.DateTimeField(null=True, blank=True)
    date_fin = models.DateTimeField(null=True, blank=True)
    
    # Champ calculé
    distance_parcourue = models.PositiveIntegerField(null=True, blank=True)
    
    def __str__(self):
        return f"Course {self.id} - {self.demandeur.username} - {self.statut}"
    
    def save(self, *args, **kwargs):
        # Calcul de la distance parcourue
        if self.kilometrage_fin and self.kilometrage_depart:
            self.distance_parcourue = self.kilometrage_fin - self.kilometrage_depart
        
        # Mise à jour des dates
        if self.statut == 'validee' and not self.date_validation:
            self.date_validation = timezone.now()
        
        if self.statut == 'en_cours' and not self.date_depart:
            self.date_depart = timezone.now()
        
        if self.statut == 'terminee' and not self.date_fin:
            self.date_fin = timezone.now()
        
        super().save(*args, **kwargs)

class ActionTraceur(models.Model):
    """Modèle pour tracer toutes les actions dans le système"""
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    date_action = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.utilisateur.username} - {self.action} - {self.date_action}"
