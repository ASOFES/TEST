import os
import django

# Configurer l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_vehicules.settings')
django.setup()

from core.models import Utilisateur

def create_admin_user():
    # Vérifier si l'utilisateur admin existe déjà
    if Utilisateur.objects.filter(username='admin').exists():
        print("L'utilisateur admin existe déjà.")
        return
    
    # Créer un nouvel utilisateur admin
    admin_user = Utilisateur.objects.create_user(
        username='admin',
        email='admin@mamo.com',
        password='Admin@123',
        first_name='Admin',
        last_name='MAMO',
        role='admin'
    )
    
    # Donner les permissions de superuser
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.save()
    
    print("Utilisateur admin créé avec succès!")
    print("Nom d'utilisateur: admin")
    print("Mot de passe: Admin@123")
    print("Rôle: Administrateur")

if __name__ == '__main__':
    create_admin_user()
