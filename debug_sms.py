import os
from twilio.rest import Client
from django.conf import settings
import django

# Initialiser Django pour accéder aux paramètres
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_vehicules.settings')
django.setup()

def test_sms():
    """Test l'envoi de SMS via Twilio"""
    print("=== DIAGNOSTIC TWILIO SMS ===")
    print(f"TWILIO_ACCOUNT_SID: {settings.TWILIO_ACCOUNT_SID}")
    print(f"TWILIO_AUTH_TOKEN: {'*' * len(settings.TWILIO_AUTH_TOKEN)} (masqué)")
    print(f"TWILIO_PHONE_NUMBER: {settings.TWILIO_PHONE_NUMBER}")
    
    # Numéro de test (votre propre numéro)
    test_number = "+243995178105"  # Votre numéro de téléphone personnel
    
    print(f"Numéro d'envoi: {settings.TWILIO_PHONE_NUMBER}")
    print(f"Numéro de réception: {test_number}")
    
    try:
        # Initialiser le client Twilio
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        print("Client Twilio initialisé avec succès.")
        
        # Envoyer un SMS de test
        print(f"Tentative d'envoi d'un SMS à {test_number}...")
        message = client.messages.create(
            body="Test de SMS depuis l'application de gestion de flotte",
            from_=settings.TWILIO_PHONE_NUMBER,
            to=test_number
        )
        
        print(f"SMS envoyé avec succès! SID du message: {message.sid}")
        return True
    except Exception as e:
        print(f"ERREUR: {str(e)}")
        return False

if __name__ == "__main__":
    test_sms() 