import os
import django

# Initialiser Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_vehicules.settings')
django.setup()

from core.models import Utilisateur

def check_users():
    """Vérifie les utilisateurs et leurs numéros de téléphone"""
    print("\n=== VÉRIFICATION DES UTILISATEURS ===")
    
    # Compter les utilisateurs par rôle
    roles = Utilisateur.objects.values_list('role', flat=True).distinct()
    for role in roles:
        count = Utilisateur.objects.filter(role=role).count()
        print(f"Rôle '{role}': {count} utilisateurs")
    
    # Vérifier les utilisateurs avec téléphone
    users_with_phone = Utilisateur.objects.exclude(telephone__isnull=True).exclude(telephone='')
    print(f"\nUtilisateurs avec numéro de téléphone: {users_with_phone.count()}")
    
    for user in users_with_phone:
        print(f"- {user.get_full_name()} ({user.role}) - Téléphone: {user.telephone}")
        
        # Vérifier le format du téléphone
        if not user.telephone.startswith('+'):
            print(f"  ⚠️ Le téléphone ne commence pas par '+', format E.164 requis")
    
    # Vérifier les préférences de notification
    from notifications.models import NotificationConfig
    configs = NotificationConfig.objects.all()
    print(f"\nConfigurations de notification: {configs.count()}")
    
    for config in configs:
        print(f"- {config.utilisateur.get_full_name()} ({config.utilisateur.role}):")
        print(f"  SMS: {'✓' if config.sms_enabled else '✗'}, "
              f"WhatsApp: {'✓' if config.whatsapp_enabled else '✗'}, "
              f"Email: {'✓' if config.email_enabled else '✗'}")

if __name__ == "__main__":
    check_users() 