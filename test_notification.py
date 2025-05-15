import os
import django
import sys
import argparse

# Configurer l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_vehicules.settings')
django.setup()

# Importer après l'initialisation de Django
from django.conf import settings
from notifications.utils import (
    send_sms_twilio, send_whatsapp_twilio,
    send_sms_cequens, send_whatsapp_cequens,
    notify_user
)
from core.models import Utilisateur

def parse_args():
    """Analyse les arguments de ligne de commande"""
    parser = argparse.ArgumentParser(description='Test des notifications')
    parser.add_argument('--provider', '-p', choices=['twilio', 'cequens', 'both'], default='both',
                      help='Fournisseur à utiliser (twilio, cequens, both)')
    parser.add_argument('--type', '-t', choices=['sms', 'whatsapp', 'both'], default='both',
                      help='Type de notification (sms, whatsapp, both)')
    parser.add_argument('--number', '-n', default=None,
                      help='Numéro de téléphone pour le test (format E.164)')
    parser.add_argument('--user', '-u', default=None,
                      help='ID ou email de l\'utilisateur à notifier')
    return parser.parse_args()

def test_twilio(test_number, notification_types):
    """Test l'envoi de notifications via Twilio"""
    print("\n=== TEST TWILIO ===")
    
    # Vérifier la configuration Twilio
    print(f"TWILIO_ACCOUNT_SID: {settings.TWILIO_ACCOUNT_SID}")
    print(f"TWILIO_AUTH_TOKEN: {'*' * len(settings.TWILIO_AUTH_TOKEN)} (masqué)")
    print(f"TWILIO_PHONE_NUMBER: {settings.TWILIO_PHONE_NUMBER}")
    print(f"TWILIO_WHATSAPP_NUMBER: {settings.TWILIO_WHATSAPP_NUMBER}")
    
    print(f"\nNuméro de test: {test_number}")
    results = {}
    
    # Test SMS
    if notification_types in ['sms', 'both']:
        print("\n--- TEST SMS TWILIO ---")
        sms_result = send_sms_twilio(
            test_number, 
            "Ceci est un test de SMS envoyé via Twilio depuis l'application de gestion de flotte."
        )
        print(f"Résultat SMS: {'Succès' if sms_result else 'Échec'}")
        results['sms'] = sms_result
    
    # Test WhatsApp
    if notification_types in ['whatsapp', 'both']:
        print("\n--- TEST WHATSAPP TWILIO ---")
        whatsapp_result = send_whatsapp_twilio(
            test_number,
            "Ceci est un test de WhatsApp envoyé via Twilio depuis l'application de gestion de flotte.\n\nPour continuer à recevoir des messages WhatsApp, veuillez répondre à ce message."
        )
        print(f"Résultat WhatsApp: {'Succès' if whatsapp_result else 'Échec'}")
        results['whatsapp'] = whatsapp_result
        
        print("\n=== RAPPEL IMPORTANT ===")
        print("Pour recevoir les messages WhatsApp dans le sandbox Twilio:")
        print("1. Enregistrez le numéro +14155238886 dans vos contacts")
        print("2. Envoyez le message 'join bright-king' à ce numéro via WhatsApp")
        print("3. Une fois inscrit, vous recevrez les notifications pendant 72 heures")
        print("4. Après 72 heures, vous devrez renvoyer le message 'join bright-king'")
    
    return results

def test_cequens(test_number, notification_types):
    """Test l'envoi de notifications via CEQUENS"""
    print("\n=== TEST CEQUENS ===")
    
    # Vérifier la configuration CEQUENS
    print(f"CEQUENS_API_KEY: {settings.CEQUENS_API_KEY}")
    print(f"CEQUENS_API_SECRET: {'*' * len(settings.CEQUENS_API_SECRET)} (masqué)")
    print(f"CEQUENS_SENDER_ID: {settings.CEQUENS_SENDER_ID}")
    print(f"CEQUENS_WHATSAPP_NUMBER: {settings.CEQUENS_WHATSAPP_NUMBER}")
    
    print(f"\nNuméro de test: {test_number}")
    results = {}
    
    # Test SMS
    if notification_types in ['sms', 'both']:
        print("\n--- TEST SMS CEQUENS ---")
        sms_result = send_sms_cequens(
            test_number, 
            "Ceci est un test de SMS envoyé via CEQUENS depuis l'application de gestion de flotte."
        )
        print(f"Résultat SMS: {'Succès' if sms_result else 'Échec'}")
        results['sms'] = sms_result
    
    # Test WhatsApp
    if notification_types in ['whatsapp', 'both']:
        print("\n--- TEST WHATSAPP CEQUENS ---")
        whatsapp_result = send_whatsapp_cequens(
            test_number,
            "Ceci est un test de WhatsApp envoyé via CEQUENS depuis l'application de gestion de flotte."
        )
        print(f"Résultat WhatsApp: {'Succès' if whatsapp_result else 'Échec'}")
        results['whatsapp'] = whatsapp_result
    
    return results

def test_user_notification(user_id_or_email, notification_types):
    """Test l'envoi de notifications à un utilisateur via le système de notification"""
    print("\n=== TEST NOTIFICATION UTILISATEUR ===")
    
    # Rechercher l'utilisateur
    user = None
    if user_id_or_email.isdigit():
        try:
            user = Utilisateur.objects.get(id=int(user_id_or_email))
        except Utilisateur.DoesNotExist:
            print(f"Utilisateur avec ID {user_id_or_email} non trouvé")
            return None
    else:
        try:
            user = Utilisateur.objects.get(email=user_id_or_email)
        except Utilisateur.DoesNotExist:
            print(f"Utilisateur avec email {user_id_or_email} non trouvé")
            return None
    
    print(f"Utilisateur trouvé: {user.get_full_name()} (ID: {user.id})")
    print(f"Email: {user.email}")
    print(f"Téléphone: {user.telephone}")
    print(f"Rôle: {user.role}")
    
    # Envoyer la notification
    title = "Test de notification"
    message = "Ceci est un test de notification depuis l'application de gestion de flotte."
    
    results = notify_user(
        user=user,
        title=title,
        message=message,
        notification_type=notification_types if notification_types != 'both' else 'all'
    )
    
    print("\nRésultats de l'envoi:")
    for notif_type, result in results.items():
        success = result if isinstance(result, bool) else result.get('success', False)
        print(f"  {notif_type}: {'Succès' if success else 'Échec'}")
    
    return results

def main():
    """Fonction principale"""
    args = parse_args()
    
    # Définir le numéro de test
    test_number = args.number if args.number else "+243995178105"
    
    # Afficher la configuration actuelle
    print("=== CONFIGURATION ACTUELLE ===")
    print(f"Fournisseur par défaut: {getattr(settings, 'MESSAGING_PROVIDER', 'TWILIO')}")
    
    results = {}
    
    # Test avec un utilisateur spécifique
    if args.user:
        results['user'] = test_user_notification(args.user, args.type)
    else:
        # Test direct avec les fournisseurs
        if args.provider in ['twilio', 'both']:
            results['twilio'] = test_twilio(test_number, args.type)
        
        if args.provider in ['cequens', 'both']:
            results['cequens'] = test_cequens(test_number, args.type)
    
    print("\n=== RÉSUMÉ DES TESTS ===")
    for provider, provider_results in results.items():
        if provider == 'user':
            print(f"Notification utilisateur: {', '.join([f'{k}: {'Succès' if v else 'Échec'}' for k, v in provider_results.items()])}")
        else:
            print(f"{provider.capitalize()}: {', '.join([f'{k}: {'Succès' if v else 'Échec'}' for k, v in provider_results.items()])}")

if __name__ == "__main__":
    main() 