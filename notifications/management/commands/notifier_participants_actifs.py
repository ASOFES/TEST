from django.core.management.base import BaseCommand
from notifications.utils import notify_active_courses_participants

class Command(BaseCommand):
    help = 'Envoie une notification à tous les utilisateurs impliqués dans des courses actives'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['sms', 'whatsapp', 'email', 'all'],
            default='all',
            help='Type de notification à envoyer (sms, whatsapp, email, all)'
        )
        
        parser.add_argument(
            '--titre',
            type=str,
            default='Notification ASOFES',
            help='Titre de la notification'
        )
        
        parser.add_argument(
            '--message',
            type=str,
            required=True,
            help='Message à envoyer aux participants'
        )

    def handle(self, *args, **options):
        notification_type = options['type']
        title = options['titre']
        message = options['message']
        
        self.stdout.write(f"Envoi de notification ({notification_type}) à tous les utilisateurs impliqués dans des courses actives")
        self.stdout.write(f"Titre: {title}")
        self.stdout.write(f"Message: {message[:50]}..." if len(message) > 50 else f"Message: {message}")
        
        # Envoyer la notification aux participants des courses actives
        results = notify_active_courses_participants(
            title=title,
            message=message,
            notification_type=notification_type
        )
        
        # Analyser les résultats
        total_users = len(results)
        if total_users == 0:
            self.stdout.write(self.style.WARNING("Aucun utilisateur impliqué dans des courses actives"))
            return
        
        # Compter les succès pour chaque type de notification
        success_count = {
            'sms': 0,
            'whatsapp': 0,
            'email': 0
        }
        
        for user_id, user_results in results.items():
            for notif_type, result in user_results.items():
                if notif_type == 'sms' and result:
                    success_count['sms'] += 1
                elif notif_type == 'whatsapp' and result:
                    success_count['whatsapp'] += 1
                elif notif_type == 'email' and result.get('success', False):
                    success_count['email'] += 1
        
        # Afficher les résultats
        self.stdout.write(self.style.SUCCESS(f"Notification envoyée à {total_users} utilisateurs impliqués dans des courses actives"))
        
        if notification_type == 'sms' or notification_type == 'all':
            self.stdout.write(f"SMS: {success_count['sms']}/{total_users} envoyés avec succès")
            
        if notification_type == 'whatsapp' or notification_type == 'all':
            self.stdout.write(f"WhatsApp: {success_count['whatsapp']}/{total_users} envoyés avec succès")
            
        if notification_type == 'email' or notification_type == 'all':
            self.stdout.write(f"Email: {success_count['email']}/{total_users} envoyés avec succès") 