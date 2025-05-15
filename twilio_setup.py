"""
Script pour configurer les identifiants CEQUENS dans le fichier settings.py
"""
import os
import re

def configurer_cequens():
    print("Configuration des identifiants CEQUENS")
    print("------------------------------------")
    print("Veuillez saisir vos identifiants CEQUENS :")
    
    api_key = input("API Key CEQUENS : ")
    api_secret = input("API Secret CEQUENS : ")
    sender_id = input("Sender ID pour SMS (nom d'expéditeur) : ")
    whatsapp_number = input("Numéro WhatsApp Business (format E.164, ex: +12345678901) : ")
    
    # Valider les entrées
    if not api_key or not api_secret:
        print("Attention: L'API Key et l'API Secret sont obligatoires")
    
    if not whatsapp_number.startswith('+'):
        print("Attention: Le numéro WhatsApp doit être au format E.164 et commencer par '+'")
        whatsapp_number = '+' + whatsapp_number
    
    # Mettre à jour le fichier settings.py
    settings_path = os.path.join('gestion_vehicules', 'settings.py')
    
    try:
        with open(settings_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Vérifier si les variables CEQUENS existent déjà
        if 'CEQUENS_API_KEY' not in content:
            # Ajouter les nouvelles variables CEQUENS après les variables Twilio
            twilio_section = re.search(r"# Twilio configuration.*?TWILIO_WHATSAPP_NUMBER = .*?\n", 
                                     content, re.DOTALL)
            if twilio_section:
                twilio_section_text = twilio_section.group(0)
                cequens_config = f"""
# CEQUENS configuration
CEQUENS_API_KEY = os.environ.get('CEQUENS_API_KEY', '{api_key}')
CEQUENS_API_SECRET = os.environ.get('CEQUENS_API_SECRET', '{api_secret}')
CEQUENS_SENDER_ID = os.environ.get('CEQUENS_SENDER_ID', '{sender_id}')
CEQUENS_WHATSAPP_NUMBER = os.environ.get('CEQUENS_WHATSAPP_NUMBER', '{whatsapp_number}')
MESSAGING_PROVIDER = os.environ.get('MESSAGING_PROVIDER', 'CEQUENS')  # Options: 'TWILIO', 'CEQUENS'
"""
                content = content.replace(twilio_section_text, twilio_section_text + cequens_config)
            else:
                # Si la section Twilio n'est pas trouvée, ajouter à la fin du fichier
                content += f"""
# CEQUENS configuration
CEQUENS_API_KEY = os.environ.get('CEQUENS_API_KEY', '{api_key}')
CEQUENS_API_SECRET = os.environ.get('CEQUENS_API_SECRET', '{api_secret}')
CEQUENS_SENDER_ID = os.environ.get('CEQUENS_SENDER_ID', '{sender_id}')
CEQUENS_WHATSAPP_NUMBER = os.environ.get('CEQUENS_WHATSAPP_NUMBER', '{whatsapp_number}')
MESSAGING_PROVIDER = os.environ.get('MESSAGING_PROVIDER', 'CEQUENS')  # Options: 'TWILIO', 'CEQUENS'
"""
        else:
            # Mettre à jour les variables CEQUENS existantes
            content = re.sub(r"CEQUENS_API_KEY = os\.environ\.get\('CEQUENS_API_KEY', '.*?'\)",
                            f"CEQUENS_API_KEY = os.environ.get('CEQUENS_API_KEY', '{api_key}')",
                            content)
            
            content = re.sub(r"CEQUENS_API_SECRET = os\.environ\.get\('CEQUENS_API_SECRET', '.*?'\)",
                            f"CEQUENS_API_SECRET = os.environ.get('CEQUENS_API_SECRET', '{api_secret}')",
                            content)
            
            content = re.sub(r"CEQUENS_SENDER_ID = os\.environ\.get\('CEQUENS_SENDER_ID', '.*?'\)",
                            f"CEQUENS_SENDER_ID = os.environ.get('CEQUENS_SENDER_ID', '{sender_id}')",
                            content)
            
            content = re.sub(r"CEQUENS_WHATSAPP_NUMBER = os\.environ\.get\('CEQUENS_WHATSAPP_NUMBER', '.*?'\)",
                            f"CEQUENS_WHATSAPP_NUMBER = os.environ.get('CEQUENS_WHATSAPP_NUMBER', '{whatsapp_number}')",
                            content)
            
            # Définir CEQUENS comme fournisseur par défaut
            content = re.sub(r"MESSAGING_PROVIDER = os\.environ\.get\('MESSAGING_PROVIDER', '.*?'\)",
                            f"MESSAGING_PROVIDER = os.environ.get('MESSAGING_PROVIDER', 'CEQUENS')",
                            content)
        
        with open(settings_path, 'w', encoding='utf-8') as file:
            file.write(content)
        
        print("\nConfiguration terminée avec succès!")
        print("Les identifiants CEQUENS ont été mis à jour dans le fichier settings.py")
        print("\nPour tester, redémarrez le serveur Django et essayez d'envoyer une notification.")
        
    except Exception as e:
        print(f"Erreur lors de la mise à jour du fichier settings.py: {str(e)}")

if __name__ == "__main__":
    configurer_cequens() 