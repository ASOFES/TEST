import os
import django
import sys

# Configurer l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_vehicules.settings')
django.setup()

# Importer après l'initialisation de Django
from django.conf import settings
from notifications.utils import send_sms_twilio, send_whatsapp_twilio

def test_twilio():
    """Test l'envoi de notifications via Twilio"""
    print("=== TEST TWILIO ===")
    
    # Vérifier la configuration Twilio
    print(f"TWILIO_ACCOUNT_SID: {settings.TWILIO_ACCOUNT_SID}")
    print(f"TWILIO_AUTH_TOKEN: {'*' * len(settings.TWILIO_AUTH_TOKEN)} (masqué)")
    print(f"TWILIO_PHONE_NUMBER: {settings.TWILIO_PHONE_NUMBER}")
    print(f"TWILIO_WHATSAPP_NUMBER: {settings.TWILIO_WHATSAPP_NUMBER}")
    
    # Numéro de test (par défaut ou fourni en argument)
    test_number = sys.argv[1] if len(sys.argv) > 1 else "+243995178105"
    
    print(f"\nNuméro de test: {test_number}")
    
    # Test SMS
    print("\n--- TEST SMS TWILIO ---")
    sms_result = send_sms_twilio(
        test_number, 
        "Ceci est un test de SMS envoyé via Twilio depuis l'application de gestion de flotte."
    )
    print(f"Résultat SMS: {'Succès' if sms_result else 'Échec'}")
    
    # Test WhatsApp
    print("\n--- TEST WHATSAPP TWILIO ---")
    whatsapp_result = send_whatsapp_twilio(
        test_number,
        "Ceci est un test de WhatsApp envoyé via Twilio depuis l'application de gestion de flotte.\n\nPour continuer à recevoir des messages WhatsApp, veuillez répondre à ce message."
    )
    print(f"Résultat WhatsApp: {'Succès' if whatsapp_result else 'Échec'}")
    
    print("\n=== RAPPEL IMPORTANT ===")
    print("Pour recevoir les messages WhatsApp dans le sandbox Twilio:")
    print("1. Enregistrez le numéro +14155238886 dans vos contacts")
    print("2. Envoyez le message 'join bright-king' à ce numéro via WhatsApp")
    print("3. Une fois inscrit, vous recevrez les notifications pendant 72 heures")
    print("4. Après 72 heures, vous devrez renvoyer le message 'join bright-king'")
    
    return sms_result, whatsapp_result

if __name__ == "__main__":
    test_twilio() 