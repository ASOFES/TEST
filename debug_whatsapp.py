import os
import requests
import json
from django.conf import settings
import django

# Initialiser Django pour accéder aux paramètres
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_vehicules.settings')
django.setup()

def test_whatsapp():
    """Test l'envoi de message WhatsApp via CEQUENS"""
    print("=== DIAGNOSTIC CEQUENS WHATSAPP ===")
    print(f"CEQUENS_API_KEY: {settings.CEQUENS_API_KEY}")
    print(f"CEQUENS_API_SECRET: {'*' * len(settings.CEQUENS_API_SECRET)} (masqué)")
    print(f"CEQUENS_WHATSAPP_NUMBER: {settings.CEQUENS_WHATSAPP_NUMBER}")
    
    # Numéro de test (votre propre numéro)
    test_number = "+243995178105"  # Votre numéro de téléphone personnel
    
    print(f"Numéro d'envoi (WhatsApp): {settings.CEQUENS_WHATSAPP_NUMBER}")
    print(f"Numéro de réception: {test_number}")
    
    try:
        # Préparer la requête pour l'API CEQUENS WhatsApp
        url = "https://apis.cequens.com/conversation/wab/v1/messages/"
        
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {settings.CEQUENS_API_KEY}"
        }
        
        # Message de test
        message = "Ceci est un message de test depuis l'application de gestion de flotte via CEQUENS WhatsApp Business API."
        
        payload = {
            "type": "text",
            "recipient_type": "individual",
            "to": test_number.replace("+", ""),  # Format sans le +
            "from": settings.CEQUENS_WHATSAPP_NUMBER.replace("+", ""),  # Format sans le +
            "text": {
                "body": message
            }
        }
        
        print("Client CEQUENS WhatsApp initialisé avec succès.")
        print(f"Tentative d'envoi d'un message WhatsApp à {test_number}...")
        
        # Envoyer la requête
        response = requests.post(url, headers=headers, json=payload)
        
        # Vérifier la réponse
        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            print(f"Message WhatsApp envoyé avec succès! ID du message: {result.get('messages', [{}])[0].get('id', 'N/A')}")
            print(f"Réponse complète: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"ERREUR: Statut {response.status_code}")
            print(f"Détails: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERREUR: {str(e)}")
        return False

if __name__ == "__main__":
    test_whatsapp() 