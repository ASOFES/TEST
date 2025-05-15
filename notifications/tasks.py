from django.utils import timezone
from datetime import timedelta
from core.models import Vehicule, Utilisateur
from .utils import notify_user

def check_document_expirations():
    """Vérifie les expirations de documents et envoie des notifications"""
    today = timezone.now().date()
    
    # Vérifier les expirations à 30, 15, 7 et 1 jour(s)
    alert_days = [30, 15, 7, 1]
    
    # Récupérer les administrateurs et dispatchers pour les notifications
    admins = Utilisateur.objects.filter(role='admin', is_active=True)
    dispatchers = Utilisateur.objects.filter(role='dispatch', is_active=True)
    
    # Liste des destinataires
    recipients = list(admins) + list(dispatchers)
    
    # Vérifier les assurances
    for days in alert_days:
        target_date = today + timedelta(days=days)
        vehicles = Vehicule.objects.filter(date_expiration_assurance=target_date)
        
        for vehicle in vehicles:
            message = f"L'assurance du véhicule {vehicle.immatriculation} ({vehicle.marque} {vehicle.modele}) expire dans {days} jour{'s' if days > 1 else ''}."
            
            for recipient in recipients:
                if recipient.notification_config.notif_expiration_docs:
                    notify_user(
                        recipient,
                        f"Expiration d'assurance dans {days} jour{'s' if days > 1 else ''}",
                        message,
                        notification_type='all',
                        vehicule=vehicle
                    )
    
    # Vérifier les contrôles techniques
    for days in alert_days:
        target_date = today + timedelta(days=days)
        vehicles = Vehicule.objects.filter(date_expiration_controle_technique=target_date)
        
        for vehicle in vehicles:
            message = f"Le contrôle technique du véhicule {vehicle.immatriculation} ({vehicle.marque} {vehicle.modele}) expire dans {days} jour{'s' if days > 1 else ''}."
            
            for recipient in recipients:
                if recipient.notification_config.notif_expiration_docs:
                    notify_user(
                        recipient,
                        f"Expiration de contrôle technique dans {days} jour{'s' if days > 1 else ''}",
                        message,
                        notification_type='all',
                        vehicule=vehicle
                    )
    
    # Vérifier les vignettes
    for days in alert_days:
        target_date = today + timedelta(days=days)
        vehicles = Vehicule.objects.filter(date_expiration_vignette=target_date)
        
        for vehicle in vehicles:
            message = f"La vignette du véhicule {vehicle.immatriculation} ({vehicle.marque} {vehicle.modele}) expire dans {days} jour{'s' if days > 1 else ''}."
            
            for recipient in recipients:
                if recipient.notification_config.notif_expiration_docs:
                    notify_user(
                        recipient,
                        f"Expiration de vignette dans {days} jour{'s' if days > 1 else ''}",
                        message,
                        notification_type='all',
                        vehicule=vehicle
                    )
    
    # Vérifier les stationnements
    for days in alert_days:
        target_date = today + timedelta(days=days)
        vehicles = Vehicule.objects.filter(date_expiration_stationnement=target_date)
        
        for vehicle in vehicles:
            message = f"Le stationnement du véhicule {vehicle.immatriculation} ({vehicle.marque} {vehicle.modele}) expire dans {days} jour{'s' if days > 1 else ''}."
            
            for recipient in recipients:
                if recipient.notification_config.notif_expiration_docs:
                    notify_user(
                        recipient,
                        f"Expiration de stationnement dans {days} jour{'s' if days > 1 else ''}",
                        message,
                        notification_type='all',
                        vehicule=vehicle
                    ) 