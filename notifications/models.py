from django.db import models
from django.utils import timezone
from core.models import Utilisateur, Vehicule, Course

class NotificationConfig(models.Model):
    """Configuration des notifications par utilisateur"""
    utilisateur = models.OneToOneField(Utilisateur, on_delete=models.CASCADE, related_name='notification_config')
    sms_enabled = models.BooleanField(default=True, verbose_name="Notifications SMS")
    whatsapp_enabled = models.BooleanField(default=True, verbose_name="Notifications WhatsApp")
    email_enabled = models.BooleanField(default=True, verbose_name="Notifications Email")
    
    # Types d'événements à notifier
    notif_demande_course = models.BooleanField(default=True, verbose_name="Demandes de course")
    notif_validation_course = models.BooleanField(default=True, verbose_name="Validation de course")
    notif_expiration_docs = models.BooleanField(default=True, verbose_name="Expiration de documents")
    notif_entretien = models.BooleanField(default=True, verbose_name="Entretiens programmés")
    
    def __str__(self):
        return f"Configuration de notifications pour {self.utilisateur.username}"

class Notification(models.Model):
    """Historique des notifications envoyées"""
    TYPE_CHOICES = (
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
        ('email', 'Email'),
        ('app', 'Application'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('sent', 'Envoyé'),
        ('delivered', 'Livré'),
        ('failed', 'Échec'),
    )
    
    destinataire = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='notifications_recues')
    type_notification = models.CharField(max_length=10, choices=TYPE_CHOICES)
    titre = models.CharField(max_length=100)
    message = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    date_envoi = models.DateTimeField(null=True, blank=True)
    statut = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    erreur = models.TextField(blank=True, null=True)
    
    # Liens optionnels vers des objets concernés
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    vehicule = models.ForeignKey(Vehicule, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    
    def __str__(self):
        return f"{self.get_type_notification_display()} à {self.destinataire.username} - {self.statut}"
    
    def marquer_comme_envoye(self):
        self.statut = 'sent'
        self.date_envoi = timezone.now()
        self.save()
    
    def marquer_comme_livre(self):
        self.statut = 'delivered'
        self.save()
    
    def marquer_comme_echec(self, erreur):
        self.statut = 'failed'
        self.erreur = erreur
        self.save()
