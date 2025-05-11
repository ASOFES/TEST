import os
import django

# Configurer l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_vehicules.settings')
django.setup()

from core.models import Utilisateur

def check_admin_user():
    try:
        admin_user = Utilisateur.objects.get(username='admin')
        print(f"Détails de l'utilisateur admin:")
        print(f"Nom d'utilisateur: {admin_user.username}")
        print(f"Prénom: {admin_user.first_name}")
        print(f"Nom: {admin_user.last_name}")
        print(f"Email: {admin_user.email}")
        print(f"Rôle: {admin_user.role} ({admin_user.get_role_display()})")
        print(f"Est superutilisateur: {admin_user.is_superuser}")
        print(f"Est membre du staff: {admin_user.is_staff}")
        
        # Vérifier si l'utilisateur a le rôle d'administrateur
        if admin_user.role != 'admin' or not admin_user.is_superuser:
            print("\nL'utilisateur existe mais n'a pas tous les privilèges d'administrateur.")
            print("Mise à jour des privilèges...")
            
            admin_user.role = 'admin'
            admin_user.is_superuser = True
            admin_user.is_staff = True
            admin_user.save()
            
            print("Privilèges mis à jour avec succès!")
    except Utilisateur.DoesNotExist:
        print("L'utilisateur admin n'existe pas.")

if __name__ == '__main__':
    check_admin_user()
