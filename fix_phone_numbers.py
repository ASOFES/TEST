import os
import django

# Initialiser Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_vehicules.settings')
django.setup()

from core.models import Utilisateur

def fix_phone_numbers():
    """Corrige les numéros de téléphone pour qu'ils soient au format E.164"""
    print("\n=== CORRECTION DES NUMÉROS DE TÉLÉPHONE ===")
    
    # Récupérer tous les utilisateurs avec un numéro de téléphone
    users_with_phone = Utilisateur.objects.exclude(telephone__isnull=True).exclude(telephone='')
    
    for user in users_with_phone:
        old_phone = user.telephone
        
        # Vérifier si le format est déjà correct
        if old_phone.startswith('+'):
            print(f"- {user.get_full_name()}: {old_phone} (déjà au format E.164)")
            continue
        
        # Correction du format pour les numéros congolais
        if old_phone.startswith('0'):
            # Remplacer le 0 initial par +243
            new_phone = '+243' + old_phone[1:]
            user.telephone = new_phone
            user.save()
            print(f"- {user.get_full_name()}: {old_phone} → {new_phone}")
        else:
            # Ajouter simplement le préfixe +243
            new_phone = '+243' + old_phone
            user.telephone = new_phone
            user.save()
            print(f"- {user.get_full_name()}: {old_phone} → {new_phone}")
    
    print("\n=== VÉRIFICATION APRÈS CORRECTION ===")
    for user in Utilisateur.objects.exclude(telephone__isnull=True).exclude(telephone=''):
        print(f"- {user.get_full_name()} ({user.role}): {user.telephone}")

if __name__ == "__main__":
    fix_phone_numbers() 