import os
import django
import sys
import argparse

# Configurer l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_vehicules.settings')
django.setup()

from django.conf import settings

def parse_args():
    """Analyse les arguments de ligne de commande"""
    parser = argparse.ArgumentParser(description='Configuration des fournisseurs de messagerie')
    parser.add_argument('--provider', '-p', choices=['twilio', 'cequens'], default='twilio',
                      help='Fournisseur à configurer comme défaut (twilio, cequens)')
    parser.add_argument('--show', '-s', action='store_true',
                      help='Afficher la configuration actuelle')
    return parser.parse_args()

def show_config():
    """Affiche la configuration actuelle"""
    print("=== CONFIGURATION ACTUELLE ===")
    print(f"Fournisseur par défaut: {getattr(settings, 'MESSAGING_PROVIDER', 'TWILIO')}")
    
    # Configuration Twilio
    print("\n--- TWILIO ---")
    print(f"TWILIO_ACCOUNT_SID: {getattr(settings, 'TWILIO_ACCOUNT_SID', 'Non configuré')}")
    print(f"TWILIO_AUTH_TOKEN: {'*' * len(getattr(settings, 'TWILIO_AUTH_TOKEN', '')) if hasattr(settings, 'TWILIO_AUTH_TOKEN') else 'Non configuré'}")
    print(f"TWILIO_PHONE_NUMBER: {getattr(settings, 'TWILIO_PHONE_NUMBER', 'Non configuré')}")
    print(f"TWILIO_WHATSAPP_NUMBER: {getattr(settings, 'TWILIO_WHATSAPP_NUMBER', 'Non configuré')}")
    
    # Configuration CEQUENS
    print("\n--- CEQUENS ---")
    print(f"CEQUENS_API_KEY: {getattr(settings, 'CEQUENS_API_KEY', 'Non configuré')}")
    print(f"CEQUENS_API_SECRET: {'*' * len(getattr(settings, 'CEQUENS_API_SECRET', '')) if hasattr(settings, 'CEQUENS_API_SECRET') else 'Non configuré'}")
    print(f"CEQUENS_SENDER_ID: {getattr(settings, 'CEQUENS_SENDER_ID', 'Non configuré')}")
    print(f"CEQUENS_WHATSAPP_NUMBER: {getattr(settings, 'CEQUENS_WHATSAPP_NUMBER', 'Non configuré')}")

def update_settings_file(provider):
    """Met à jour le fichier settings.py pour définir le fournisseur par défaut"""
    settings_file = os.path.join(os.path.dirname(settings.__file__), 'settings.py')
    
    if not os.path.exists(settings_file):
        print(f"Erreur: Fichier de configuration non trouvé: {settings_file}")
        return False
    
    # Lire le fichier settings.py
    with open(settings_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier si la variable MESSAGING_PROVIDER existe déjà
    if 'MESSAGING_PROVIDER' in content:
        # Mettre à jour la valeur existante
        import re
        pattern = r"MESSAGING_PROVIDER\s*=\s*['\"]([^'\"]+)['\"]"
        replacement = f"MESSAGING_PROVIDER = '{provider.upper()}'"
        new_content = re.sub(pattern, replacement, content)
        
        if new_content == content:
            print(f"Avertissement: Impossible de trouver la variable MESSAGING_PROVIDER dans le format attendu")
            # Ajouter la variable à la fin du fichier
            new_content = content + f"\n\n# Fournisseur de messagerie par défaut (TWILIO ou CEQUENS)\nMESSAGING_PROVIDER = '{provider.upper()}'\n"
    else:
        # Ajouter la variable à la fin du fichier
        new_content = content + f"\n\n# Fournisseur de messagerie par défaut (TWILIO ou CEQUENS)\nMESSAGING_PROVIDER = '{provider.upper()}'\n"
    
    # Écrire le fichier mis à jour
    with open(settings_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Configuration mise à jour: fournisseur par défaut défini à {provider.upper()}")
    return True

def main():
    """Fonction principale"""
    args = parse_args()
    
    # Afficher la configuration actuelle
    if args.show:
        show_config()
        return
    
    # Mettre à jour le fournisseur par défaut
    update_settings_file(args.provider)
    
    # Afficher la nouvelle configuration
    print("\nNouvelle configuration:")
    show_config()

if __name__ == "__main__":
    main() 