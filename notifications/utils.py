import os
import logging
from twilio.rest import Client
from django.core.mail import send_mail
from django.conf import settings
from .models import Notification, NotificationConfig
from twilio.base.exceptions import TwilioRestException
from django.db.models import Q

logger = logging.getLogger(__name__)

# Configuration Twilio
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER', '')
TWILIO_WHATSAPP_NUMBER = os.environ.get('TWILIO_WHATSAPP_NUMBER', '')

def send_sms(to_number, message):
    """
    Envoie un SMS via Twilio
    
    Args:
        to_number (str): Numéro de téléphone du destinataire (format E.164)
        message (str): Contenu du message
    
    Returns:
        bool: True si l'envoi a réussi, False sinon
    """
    # Vérifier si les identifiants Twilio sont configurés
    if not all([
        getattr(settings, 'TWILIO_ACCOUNT_SID', None),
        getattr(settings, 'TWILIO_AUTH_TOKEN', None),
        getattr(settings, 'TWILIO_PHONE_NUMBER', None)
    ]):
        logger.error("Configuration Twilio manquante")
        print(f"[ERREUR SMS] Configuration Twilio manquante")
        return False
    
    # Log plus détaillé pour le débogage
    print(f"\n[TENTATIVE SMS] Destinataire: {to_number}")
    print(f"[TENTATIVE SMS] Expéditeur: {settings.TWILIO_PHONE_NUMBER}")
    print(f"[TENTATIVE SMS] Message: {message[:50]}...")
    
    try:
        # Initialiser le client Twilio
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        print("[TENTATIVE SMS] Client Twilio initialisé avec succès")
        
        # Envoyer le SMS
        message = client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=to_number
        )
        
        logger.info(f"SMS envoyé avec succès: {message.sid}")
        print(f"[SMS ENVOYÉ] À: {to_number} | SID: {message.sid}")
        return True
    except TwilioRestException as e:
        logger.error(f"Erreur lors de l'envoi du SMS: {str(e)}")
        print(f"[ERREUR SMS] {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Erreur inattendue lors de l'envoi du SMS: {str(e)}")
        print(f"[ERREUR SMS] {str(e)}")
        return False

def send_whatsapp(to_number, message):
    """
    Envoie un message WhatsApp via Twilio
    
    Args:
        to_number (str): Numéro de téléphone du destinataire (format E.164)
        message (str): Contenu du message
    
    Returns:
        bool: True si l'envoi a réussi, False sinon
    """
    # Vérifier si les identifiants Twilio sont configurés
    if not all([
        getattr(settings, 'TWILIO_ACCOUNT_SID', None),
        getattr(settings, 'TWILIO_AUTH_TOKEN', None),
        getattr(settings, 'TWILIO_WHATSAPP_NUMBER', None)
    ]):
        logger.error("Configuration Twilio WhatsApp manquante")
        print(f"[ERREUR WHATSAPP] Configuration Twilio WhatsApp manquante")
        return False
    
    # Log plus détaillé pour le débogage
    print(f"\n[TENTATIVE WHATSAPP] Destinataire: {to_number}")
    print(f"[TENTATIVE WHATSAPP] Expéditeur: {settings.TWILIO_WHATSAPP_NUMBER}")
    print(f"[TENTATIVE WHATSAPP] Message: {message[:50]}...")
    
    try:
        # Initialiser le client Twilio
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        print("[TENTATIVE WHATSAPP] Client Twilio initialisé avec succès")
        
        # Formater les numéros pour WhatsApp
        from_whatsapp = f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}"
        to_whatsapp = f"whatsapp:{to_number}"
        
        print(f"[TENTATIVE WHATSAPP] De: {from_whatsapp}")
        print(f"[TENTATIVE WHATSAPP] À: {to_whatsapp}")
        
        # Envoyer le message WhatsApp
        message = client.messages.create(
            body=message,
            from_=from_whatsapp,
            to=to_whatsapp
        )
        
        logger.info(f"Message WhatsApp envoyé avec succès: {message.sid}")
        print(f"[WHATSAPP ENVOYÉ] À: {to_number} | SID: {message.sid}")
        return True
    except TwilioRestException as e:
        logger.error(f"Erreur lors de l'envoi du message WhatsApp: {str(e)}")
        print(f"[ERREUR WHATSAPP] {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Erreur inattendue lors de l'envoi du message WhatsApp: {str(e)}")
        print(f"[ERREUR WHATSAPP] {str(e)}")
        return False

def send_email(to_email, subject, message, html_message=None):
    """Envoie un email"""
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [to_email],
            fail_silently=False,
            html_message=html_message
        )
        return {
            'success': True
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def notify_user(user, title, message, notification_type='all', course=None, vehicule=None):
    """
    Envoie une notification à un utilisateur selon ses préférences
    notification_type: 'sms', 'whatsapp', 'email', 'all'
    """
    # Récupérer les préférences de l'utilisateur
    config, created = NotificationConfig.objects.get_or_create(utilisateur=user)
    
    results = {}
    
    # Envoyer par SMS
    if (notification_type == 'sms' or notification_type == 'all') and config.sms_enabled and user.telephone:
        notification = Notification.objects.create(
            destinataire=user,
            type_notification='sms',
            titre=title,
            message=message,
            course=course,
            vehicule=vehicule
        )
        
        result = send_sms(user.telephone, message)
        if result:
            notification.marquer_comme_envoye()
        else:
            notification.marquer_comme_echec("Erreur lors de l'envoi du SMS")
        results['sms'] = result
    
    # Envoyer par WhatsApp
    if (notification_type == 'whatsapp' or notification_type == 'all') and config.whatsapp_enabled and user.telephone:
        notification = Notification.objects.create(
            destinataire=user,
            type_notification='whatsapp',
            titre=title,
            message=message,
            course=course,
            vehicule=vehicule
        )
        
        result = send_whatsapp(user.telephone, message)
        if result:
            notification.marquer_comme_envoye()
        else:
            notification.marquer_comme_echec("Erreur lors de l'envoi du message WhatsApp")
        results['whatsapp'] = result
    
    # Envoyer par Email
    if (notification_type == 'email' or notification_type == 'all') and config.email_enabled and user.email:
        notification = Notification.objects.create(
            destinataire=user,
            type_notification='email',
            titre=title,
            message=message,
            course=course,
            vehicule=vehicule
        )
        
        result = send_email(user.email, title, message)
        if result['success']:
            notification.marquer_comme_envoye()
        else:
            notification.marquer_comme_echec(result['error'])
        results['email'] = result
    
    return results 

def notify_multiple_users(users, title, message, notification_type='all', course=None, vehicule=None):
    """
    Envoie une notification à plusieurs utilisateurs simultanément
    
    Args:
        users (list): Liste d'objets utilisateurs à notifier
        title (str): Titre de la notification
        message (str): Contenu de la notification
        notification_type (str): Type de notification ('sms', 'whatsapp', 'email', 'all')
        course (Course, optional): Objet course associé
        vehicule (Vehicule, optional): Objet véhicule associé
    
    Returns:
        dict: Résultats des notifications par utilisateur
    """
    results = {}
    
    print(f"\n[NOTIFICATION GROUPE] Envoi à {len(users)} utilisateurs")
    print(f"[NOTIFICATION GROUPE] Titre: {title}")
    print(f"[NOTIFICATION GROUPE] Type: {notification_type}")
    
    for user in users:
        print(f"[NOTIFICATION GROUPE] Envoi à {user.get_full_name()} ({user.role})")
        user_result = notify_user(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            course=course,
            vehicule=vehicule
        )
        results[user.id] = user_result
    
    return results

def notify_course_participants(course, title, message, notification_type='all'):
    """
    Envoie une notification à toutes les personnes impliquées dans une course
    
    Args:
        course (Course): Objet course
        title (str): Titre de la notification
        message (str): Contenu de la notification
        notification_type (str): Type de notification ('sms', 'whatsapp', 'email', 'all')
    
    Returns:
        dict: Résultats des notifications
    """
    participants = []
    
    # Ajouter le demandeur
    if course.demandeur:
        participants.append(course.demandeur)
    
    # Ajouter le chauffeur
    if course.chauffeur:
        participants.append(course.chauffeur)
    
    # Ajouter le dispatcher
    if course.dispatcher:
        participants.append(course.dispatcher)
    
    # Envoyer la notification à tous les participants
    return notify_multiple_users(
        users=participants,
        title=title,
        message=message,
        notification_type=notification_type,
        course=course
    )

def notify_active_courses_participants(title, message, notification_type='all'):
    """
    Envoie une notification à tous les utilisateurs impliqués dans des courses actives
    
    Args:
        title (str): Titre de la notification
        message (str): Contenu de la notification
        notification_type (str): Type de notification ('sms', 'whatsapp', 'email', 'all')
    
    Returns:
        dict: Résultats des notifications
    """
    from core.models import Course
    
    # Récupérer les utilisateurs impliqués dans des courses actives
    courses_actives = Course.objects.filter(
        Q(statut='en_attente') | Q(statut='validee') | Q(statut='en_cours')
    )
    
    print(f"\n[NOTIFICATION COURSES ACTIVES] Recherche des participants de {courses_actives.count()} courses actives")
    
    # Utilisez un ensemble pour éviter les doublons
    utilisateurs_impliques = set()
    
    # Pour chaque course active, ajouter les participants à l'ensemble
    for course in courses_actives:
        if course.demandeur:
            utilisateurs_impliques.add(course.demandeur)
        
        if course.chauffeur:
            utilisateurs_impliques.add(course.chauffeur)
        
        if course.dispatcher:
            utilisateurs_impliques.add(course.dispatcher)
    
    # Convertir l'ensemble en liste
    participants = list(utilisateurs_impliques)
    
    print(f"[NOTIFICATION COURSES ACTIVES] {len(participants)} utilisateurs identifiés comme participants")
    
    # Utiliser la fonction existante pour envoyer aux utilisateurs
    return notify_multiple_users(
        users=participants,
        title=title,
        message=message,
        notification_type=notification_type
    )

def envoyer_rappel_activation_whatsapp(user):
    """
    Envoie un rappel d'activation WhatsApp à un utilisateur
    
    Args:
        user (Utilisateur): L'utilisateur à qui envoyer le rappel
        
    Returns:
        bool: True si l'envoi a réussi, False sinon
    """
    if not user.telephone:
        print(f"[RAPPEL WHATSAPP] Utilisateur {user.get_full_name()} n'a pas de numéro de téléphone")
        return False
    
    # Message d'instruction pour l'activation
    title = "Activer les notifications WhatsApp"
    message = f"""Pour recevoir les notifications WhatsApp de notre application:

1. Enregistrez ce numéro dans vos contacts: +14155238886 (ASOFES Notifications)
2. Envoyez le message "join bright-king" via WhatsApp à ce numéro.
3. Vous recevrez une confirmation d'activation.

Veuillez noter que l'activation expire après 3 jours sans interaction. 
Si vous ne recevez plus de notifications WhatsApp, veuillez renvoyer "join bright-king" au même numéro."""
    
    # Envoyer via SMS car WhatsApp n'est pas encore activé
    try:
        print(f"[RAPPEL WHATSAPP] Envoi des instructions d'activation à {user.get_full_name()} - {user.telephone}")
        send_sms(user.telephone, message)
        return True
    except Exception as e:
        print(f"[ERREUR RAPPEL WHATSAPP] {str(e)}")
        return False

def envoyer_rappel_activation_groupe(users):
    """
    Envoie un rappel d'activation WhatsApp à un groupe d'utilisateurs
    
    Args:
        users (list): Liste d'utilisateurs à qui envoyer le rappel
        
    Returns:
        dict: Résultats des envois par utilisateur
    """
    results = {}
    print(f"\n[RAPPEL WHATSAPP GROUPE] Envoi à {len(users)} utilisateurs")
    
    for user in users:
        print(f"[RAPPEL WHATSAPP GROUPE] Traitement de {user.get_full_name()} ({user.role})")
        results[user.id] = envoyer_rappel_activation_whatsapp(user)
    
    return results 