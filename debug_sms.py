import os
import requests
import json
from django.conf import settings
import django

# Initialiser Django pour accéder aux paramètres
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_vehicules.settings')
django.setup()

def test_sms():
    """Test l'envoi de SMS via CEQUENS"""
    print("=== DIAGNOSTIC CEQUENS SMS ===")
    print(f"CEQUENS_API_KEY: {settings.CEQUENS_API_KEY}")
    print(f"CEQUENS_API_SECRET: {'*' * len(settings.CEQUENS_API_SECRET)} (masqué)")
    print(f"CEQUENS_SENDER_ID: {settings.CEQUENS_SENDER_ID}")
    
    # Numéro de test (votre propre numéro)
    test_number = "+243995178105"  # Votre numéro de téléphone personnel
    
    print(f"Sender ID: {settings.CEQUENS_SENDER_ID}")
    print(f"Numéro de réception: {test_number}")
    
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
            "recipients": [test_number],
            "messageBody": "Test de SMS depuis l'application de gestion de flotte via CEQUENS"
        }
        
        print("Client CEQUENS initialisé avec succès.")
        print(f"Tentative d'envoi d'un SMS à {test_number}...")
        
        # Envoyer la requête
        response = requests.post(url, headers=headers, json=payload)
        
        # Vérifier la réponse
        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            print(f"SMS envoyé avec succès! ID du message: {result.get('messageId', 'N/A')}")
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
    test_sms() 