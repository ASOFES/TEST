import os
from twilio.rest import Client
from django.conf import settings
import django

# Initialiser Django pour accéder aux paramètres
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_vehicules.settings')
django.setup()

def test_whatsapp():
    """Test l'envoi de message WhatsApp via Twilio"""
    print("=== DIAGNOSTIC TWILIO WHATSAPP ===")
    print(f"TWILIO_ACCOUNT_SID: {settings.TWILIO_ACCOUNT_SID}")
    print(f"TWILIO_AUTH_TOKEN: {'*' * len(settings.TWILIO_AUTH_TOKEN)} (masqué)")
    print(f"TWILIO_WHATSAPP_NUMBER: {settings.TWILIO_WHATSAPP_NUMBER}")
    
    # Numéro de test (votre propre numéro)
    test_number = "+243995178105"  # Votre numéro de téléphone personnel
    
    print(f"Numéro d'envoi (WhatsApp): {settings.TWILIO_WHATSAPP_NUMBER}")
    print(f"Numéro de réception: {test_number}")
    
    try:
        # Initialiser le client Twilio
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        print("Client Twilio initialisé avec succès.")
        
        # Formater les numéros pour WhatsApp
        from_whatsapp = f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}"
        to_whatsapp = f"whatsapp:{test_number}"
        
        # Message template avec instructions pour l'activation
        message = """Ceci est un message de test depuis l'application de gestion de flotte.

Pour recevoir des messages WhatsApp de notre application, vous devez d'abord:
1. Enregistrer ce numéro dans vos contacts: +14155238886
2. Envoyer "join bright-king" via WhatsApp à ce numéro.

Après cela, vous pourrez recevoir nos notifications par WhatsApp."""
        
        # Envoyer un message WhatsApp de test
        print(f"Tentative d'envoi d'un message WhatsApp à {to_whatsapp}...")
        message = client.messages.create(
            body=message,
            from_=from_whatsapp,
            to=to_whatsapp
        )
        
        print(f"Message WhatsApp envoyé avec succès! SID du message: {message.sid}")
        print("\n===== IMPORTANT =====")
        print("Pour recevoir les messages WhatsApp dans le sandbox Twilio:")
        print("1. Enregistrez le numéro +14155238886 dans vos contacts")
        print("2. Envoyez le message 'join bright-king' à ce numéro via WhatsApp")
        print("3. Une fois inscrit, vous recevrez les notifications pendant 72 heures")
        print("4. Après 72 heures, vous devrez renvoyer le message 'join bright-king'")
        return True
    except Exception as e:
        print(f"ERREUR: {str(e)}")
        return False

if __name__ == "__main__":
    test_whatsapp() 