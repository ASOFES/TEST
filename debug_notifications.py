import os
import django

# Configurer l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_vehicules.settings')
django.setup()

from core.models import Course, Utilisateur
from notifications.models import Notification, NotificationConfig
from notifications.utils import notify_user, notify_course_participants
from django.db.models import Q
import sys

def main():
    print("\n=== DIAGNOSTIC DU SYSTÈME DE NOTIFICATIONS ===")

    # Vérifier les courses actives
    courses_actives = Course.objects.filter(
        Q(statut='en_attente') | Q(statut='validee') | Q(statut='en_cours')
    )
    print(f"\nCourses actives: {courses_actives.count()}")
    
    if courses_actives.count() > 0:
        print("\nDétails des courses actives:")
        for course in courses_actives:
            print(f"ID: {course.id}, Statut: {course.statut}")
            print(f"  Demandeur: {course.demandeur.get_full_name() if course.demandeur else 'Non assigné'}")
            print(f"  Chauffeur: {course.chauffeur.get_full_name() if course.chauffeur else 'Non assigné'}")
            print(f"  Dispatcher: {course.dispatcher.get_full_name() if course.dispatcher else 'Non assigné'}")
    else:
        print("Aucune course active trouvée dans le système.")

    # Vérifier les configurations de notification
    configs = NotificationConfig.objects.all()
    print(f"\nConfigurations de notification: {configs.count()}")
    
    if configs.count() > 0:
        print("\nDétails des configurations:")
        for config in configs:
            print(f"Utilisateur: {config.utilisateur.get_full_name()} ({config.utilisateur.role})")
            print(f"  SMS activé: {config.sms_enabled}")
            print(f"  WhatsApp activé: {config.whatsapp_enabled}")
            print(f"  Email activé: {config.email_enabled}")
    else:
        print("Aucune configuration de notification trouvée.")
        
    # Vérifier les notifications récentes
    notifications = Notification.objects.all().order_by('-date_creation')[:10]
    print(f"\nNotifications récentes: {Notification.objects.count()} total, affichage des 10 dernières")
    
    if notifications.count() > 0:
        print("\nDétails des notifications récentes:")
        for notif in notifications:
            print(f"ID: {notif.id}, Type: {notif.type_notification}, Statut: {notif.statut}")
            print(f"  Destinataire: {notif.destinataire.get_full_name()} ({notif.destinataire.role})")
            print(f"  Titre: {notif.titre}")
            print(f"  Date création: {notif.date_creation}")
            print(f"  Date envoi: {notif.date_envoi}")
            if notif.statut == 'failed':
                print(f"  Erreur: {notif.erreur}")
    else:
        print("Aucune notification trouvée.")
    
    # Si une course est spécifiée en argument, tester l'envoi de notification
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        course_id = int(sys.argv[1])
        try:
            course = Course.objects.get(id=course_id)
            print(f"\n=== TEST D'ENVOI DE NOTIFICATION POUR LA COURSE {course_id} ===")
            
            result = notify_course_participants(
                course=course,
                title="Test de notification de course",
                message=f"Ceci est un test de notification pour la course {course_id}",
                notification_type='all'
            )
            
            print("\nRésultat de l'envoi:")
            for user_id, user_result in result.items():
                user = Utilisateur.objects.get(id=user_id)
                print(f"Utilisateur: {user.get_full_name()} ({user.role})")
                for notif_type, notif_result in user_result.items():
                    success = notif_result if isinstance(notif_result, bool) else notif_result.get('success', False)
                    print(f"  {notif_type}: {'✓' if success else '✗'}")
        except Course.DoesNotExist:
            print(f"Course avec ID {course_id} non trouvée")

if __name__ == "__main__":
    main() 