import os
import logging
import requests
import json
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

# Configuration CEQUENS
CEQUENS_API_KEY = os.environ.get('CEQUENS_API_KEY', '')
CEQUENS_API_SECRET = os.environ.get('CEQUENS_API_SECRET', '')
CEQUENS_SENDER_ID = os.environ.get('CEQUENS_SENDER_ID', '')
CEQUENS_WHATSAPP_NUMBER = os.environ.get('CEQUENS_WHATSAPP_NUMBER', '')

def get_messaging_provider():
    """
    Retourne le fournisseur de messagerie configuré
    
    Returns:
        str: 'TWILIO' ou 'CEQUENS'
    """
    return getattr(settings, 'MESSAGING_PROVIDER', 'TWILIO')

def send_sms(to_number, message):
    """
    Envoie un SMS via le fournisseur configuré
    
    Args:
        to_number (str): Numéro de téléphone du destinataire (format E.164)
        message (str): Contenu du message
    
    Returns:
        bool: True si l'envoi a réussi, False sinon
    """
    provider = get_messaging_provider()
    
    if provider == 'CEQUENS':
        return send_sms_cequens(to_number, message)
    else:
        return send_sms_twilio(to_number, message)

def send_whatsapp(to_number, message):
    """
    Envoie un message WhatsApp via le fournisseur configuré
    
    Args:
        to_number (str): Numéro de téléphone du destinataire (format E.164)
        message (str): Contenu du message
    
    Returns:
        bool: True si l'envoi a réussi, False sinon
    """
    provider = get_messaging_provider()
    
    if provider == 'CEQUENS':
        return send_whatsapp_cequens(to_number, message)
    else:
        return send_whatsapp_twilio(to_number, message)

def send_sms_twilio(to_number, message):
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
    print(f"\n[TENTATIVE SMS TWILIO] Destinataire: {to_number}")
    print(f"[TENTATIVE SMS TWILIO] Expéditeur: {settings.TWILIO_PHONE_NUMBER}")
    print(f"[TENTATIVE SMS TWILIO] Message: {message[:50]}...")
    
    try:
        # Initialiser le client Twilio
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        print("[TENTATIVE SMS TWILIO] Client Twilio initialisé avec succès")
        
        # Envoyer le SMS
        message = client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=to_number
        )
        
        logger.info(f"SMS envoyé avec succès via Twilio: {message.sid}")
        print(f"[SMS TWILIO ENVOYÉ] À: {to_number} | SID: {message.sid}")
        return True
    except TwilioRestException as e:
        logger.error(f"Erreur lors de l'envoi du SMS via Twilio: {str(e)}")
        print(f"[ERREUR SMS TWILIO] {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Erreur inattendue lors de l'envoi du SMS via Twilio: {str(e)}")
        print(f"[ERREUR SMS TWILIO] {str(e)}")
        return False

def send_sms_cequens(to_number, message):
    """
    Envoie un SMS via CEQUENS
    
    Args:
        to_number (str): Numéro de téléphone du destinataire (format E.164)
        message (str): Contenu du message
    
    Returns:
        bool: True si l'envoi a réussi, False sinon
    """
    # Vérifier si les identifiants CEQUENS sont configurés
    if not all([
        getattr(settings, 'CEQUENS_API_KEY', None),
        getattr(settings, 'CEQUENS_API_SECRET', None),
        getattr(settings, 'CEQUENS_SENDER_ID', None)
    ]):
        logger.error("Configuration CEQUENS manquante")
        print(f"[ERREUR SMS] Configuration CEQUENS manquante")
        return False
    
    # Log plus détaillé pour le débogage
    print(f"\n[TENTATIVE SMS CEQUENS] Destinataire: {to_number}")
    print(f"[TENTATIVE SMS CEQUENS] Expéditeur: {settings.CEQUENS_SENDER_ID}")
    print(f"[TENTATIVE SMS CEQUENS] Message: {message[:50]}...")
    
    try:
        # Préparer la requête pour l'API CEQUENS
        url = "https://apis.cequens.com/sms/v1/messages"
        
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {settings.CEQUENS_API_KEY}"
        }
        
        payload = {
            "senderName": settings.CEQUENS_SENDER_ID,
            "messageType": "text",
            "shortURL": False,
            "recipients": [to_number],
            "messageBody": message
        }
        
        print("[TENTATIVE SMS CEQUENS] Préparation de la requête API réussie")
        
        # Envoyer la requête
        response = requests.post(url, headers=headers, json=payload)
        
        # Vérifier la réponse
        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            message_id = result.get('messageId', 'N/A')
            logger.info(f"SMS envoyé avec succès via CEQUENS: {message_id}")
            print(f"[SMS CEQUENS ENVOYÉ] À: {to_number} | ID: {message_id}")
            return True
        else:
            logger.error(f"Erreur lors de l'envoi du SMS via CEQUENS: {response.status_code} - {response.text}")
            print(f"[ERREUR SMS CEQUENS] Statut: {response.status_code}, Détails: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Erreur inattendue lors de l'envoi du SMS via CEQUENS: {str(e)}")
        print(f"[ERREUR SMS CEQUENS] {str(e)}")
        return False

def send_whatsapp_twilio(to_number, message):
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
    print(f"\n[TENTATIVE WHATSAPP TWILIO] Destinataire: {to_number}")
    print(f"[TENTATIVE WHATSAPP TWILIO] Expéditeur: {settings.TWILIO_WHATSAPP_NUMBER}")
    print(f"[TENTATIVE WHATSAPP TWILIO] Message: {message[:50]}...")
    
    try:
        # Initialiser le client Twilio
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        print("[TENTATIVE WHATSAPP TWILIO] Client Twilio initialisé avec succès")
        
        # Formater les numéros pour WhatsApp
        from_whatsapp = f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}"
        to_whatsapp = f"whatsapp:{to_number}"
        
        print(f"[TENTATIVE WHATSAPP TWILIO] De: {from_whatsapp}")
        print(f"[TENTATIVE WHATSAPP TWILIO] À: {to_whatsapp}")
        
        # Envoyer le message WhatsApp
        message = client.messages.create(
            body=message,
            from_=from_whatsapp,
            to=to_whatsapp
        )
        
        logger.info(f"Message WhatsApp envoyé avec succès via Twilio: {message.sid}")
        print(f"[WHATSAPP TWILIO ENVOYÉ] À: {to_number} | SID: {message.sid}")
        return True
    except TwilioRestException as e:
        logger.error(f"Erreur lors de l'envoi du message WhatsApp via Twilio: {str(e)}")
        print(f"[ERREUR WHATSAPP TWILIO] {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Erreur inattendue lors de l'envoi du message WhatsApp via Twilio: {str(e)}")
        print(f"[ERREUR WHATSAPP TWILIO] {str(e)}")
        return False

def send_whatsapp_cequens(to_number, message):
    """
    Envoie un message WhatsApp via CEQUENS
    
    Args:
        to_number (str): Numéro de téléphone du destinataire (format E.164)
        message (str): Contenu du message
    
    Returns:
        bool: True si l'envoi a réussi, False sinon
    """
    # Vérifier si les identifiants CEQUENS sont configurés
    if not all([
        getattr(settings, 'CEQUENS_API_KEY', None),
        getattr(settings, 'CEQUENS_API_SECRET', None),
        getattr(settings, 'CEQUENS_WHATSAPP_NUMBER', None)
    ]):
        logger.error("Configuration CEQUENS WhatsApp manquante")
        print(f"[ERREUR WHATSAPP] Configuration CEQUENS WhatsApp manquante")
        return False
    
    # Log plus détaillé pour le débogage
    print(f"\n[TENTATIVE WHATSAPP CEQUENS] Destinataire: {to_number}")
    print(f"[TENTATIVE WHATSAPP CEQUENS] Expéditeur: {settings.CEQUENS_WHATSAPP_NUMBER}")
    print(f"[TENTATIVE WHATSAPP CEQUENS] Message: {message[:50]}...")
    
    try:
        # Préparer la requête pour l'API CEQUENS WhatsApp
        url = "https://apis.cequens.com/conversation/wab/v1/messages/"
        
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {settings.CEQUENS_API_KEY}"
        }
        
        # Formater les numéros pour WhatsApp (sans le +)
        from_number = settings.CEQUENS_WHATSAPP_NUMBER.replace("+", "")
        to_number_clean = to_number.replace("+", "")
        
        payload = {
            "type": "text",
            "recipient_type": "individual",
            "to": to_number_clean,
            "from": from_number,
            "text": {
                "body": message
            }
        }
        
        print("[TENTATIVE WHATSAPP CEQUENS] Préparation de la requête API réussie")
        print(f"[TENTATIVE WHATSAPP CEQUENS] De: {from_number}")
        print(f"[TENTATIVE WHATSAPP CEQUENS] À: {to_number_clean}")
        
        # Envoyer la requête
        response = requests.post(url, headers=headers, json=payload)
        
        # Vérifier la réponse
        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            message_id = result.get('messages', [{}])[0].get('id', 'N/A') if result.get('messages') else 'N/A'
            logger.info(f"Message WhatsApp envoyé avec succès via CEQUENS: {message_id}")
            print(f"[WHATSAPP CEQUENS ENVOYÉ] À: {to_number} | ID: {message_id}")
            return True
        else:
            logger.error(f"Erreur lors de l'envoi du message WhatsApp via CEQUENS: {response.status_code} - {response.text}")
            print(f"[ERREUR WHATSAPP CEQUENS] Statut: {response.status_code}, Détails: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Erreur inattendue lors de l'envoi du message WhatsApp via CEQUENS: {str(e)}")
        print(f"[ERREUR WHATSAPP CEQUENS] {str(e)}")
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
        if result.get('success'):
            notification.marquer_comme_envoye()
        else:
            notification.marquer_comme_echec(f"Erreur lors de l'envoi de l'email: {result.get('error')}")
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