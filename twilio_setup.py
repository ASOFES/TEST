"""
Script pour configurer les identifiants Twilio dans le fichier settings.py
"""
import os
import re

def configurer_twilio():
    print("Configuration des identifiants Twilio")
    print("------------------------------------")
    print("Veuillez saisir vos identifiants Twilio :")
    
    account_sid = input("Account SID (commence par AC) : ")
    auth_token = input("Auth Token : ")
    phone_number = input("Numéro de téléphone Twilio (format E.164, ex: +12345678901) : ")
    whatsapp_number = input("Numéro WhatsApp Twilio (généralement le même que le précédent) : ")
    
    # Valider les entrées
    if not account_sid.startswith('AC'):
        print("Attention: Un Account SID Twilio commence généralement par 'AC'")
    
    if not phone_number.startswith('+'):
        print("Attention: Le numéro de téléphone doit être au format E.164 et commencer par '+'")
        phone_number = '+' + phone_number
    
    if not whatsapp_number.startswith('+'):
        print("Attention: Le numéro WhatsApp doit être au format E.164 et commencer par '+'")
        whatsapp_number = '+' + whatsapp_number
    
    # Mettre à jour le fichier settings.py
    settings_path = os.path.join('gestion_vehicules', 'settings.py')
    
    try:
        with open(settings_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Remplacer les identifiants
        content = re.sub(r"TWILIO_ACCOUNT_SID = os\.environ\.get\('TWILIO_ACCOUNT_SID', '.*?'\)",
                         f"TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '{account_sid}')",
                         content)
        
        content = re.sub(r"TWILIO_AUTH_TOKEN = os\.environ\.get\('TWILIO_AUTH_TOKEN', '.*?'\)",
                         f"TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '{auth_token}')",
                         content)
        
        content = re.sub(r"TWILIO_PHONE_NUMBER = os\.environ\.get\('TWILIO_PHONE_NUMBER', '.*?'\)",
                         f"TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER', '{phone_number}')",
                         content)
        
        content = re.sub(r"TWILIO_WHATSAPP_NUMBER = os\.environ\.get\('TWILIO_WHATSAPP_NUMBER', '.*?'\)",
                         f"TWILIO_WHATSAPP_NUMBER = os.environ.get('TWILIO_WHATSAPP_NUMBER', '{whatsapp_number}')",
                         content)
        
        with open(settings_path, 'w', encoding='utf-8') as file:
            file.write(content)
        
        print("\nConfiguration terminée avec succès!")
        print("Les identifiants Twilio ont été mis à jour dans le fichier settings.py")
        print("\nPour tester, redémarrez le serveur Django et essayez d'envoyer une notification.")
        
    except Exception as e:
        print(f"Erreur lors de la mise à jour du fichier settings.py: {str(e)}")

if __name__ == "__main__":
    configurer_twilio() 