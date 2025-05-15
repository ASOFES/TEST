from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from core.models import Utilisateur
from django.db.models import Q

class Command(BaseCommand):
    help = 'Teste l\'envoi d\'emails aux utilisateurs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=int,
            help='ID de l\'utilisateur à qui envoyer l\'email de test'
        )
        
        parser.add_argument(
            '--email',
            type=str,
            help='Adresse email pour envoyer un test directement'
        )
        
        parser.add_argument(
            '--role',
            type=str,
            help='Rôle des utilisateurs à qui envoyer l\'email de test (chauffeur, dispatch, demandeur, etc.)'
        )
        
        parser.add_argument(
            '--all',
            action='store_true',
            help='Envoyer à tous les utilisateurs avec une adresse email'
        )
        
        parser.add_argument(
            '--impliques',
            action='store_true',
            help='Envoyer à tous les utilisateurs impliqués dans des courses actives'
        )
        
        parser.add_argument(
            '--subject',
            type=str,
            default="Test de notification email ASOFES",
            help='Sujet de l\'email'
        )
        
        parser.add_argument(
            '--message',
            type=str,
            default="Ceci est un message de test du système de notification email ASOFES. Si vous recevez ce message, le système fonctionne correctement.",
            help='Contenu de l\'email'
        )

    def handle(self, *args, **options):
        subject = options['subject']
        message = options['message']
        
        # Informations de débogage
        self.stdout.write(f"\n=== CONFIGURATION EMAIL ACTUELLE ===")
        self.stdout.write(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
        self.stdout.write(f"EMAIL_HOST: {settings.EMAIL_HOST}")
        self.stdout.write(f"EMAIL_PORT: {settings.EMAIL_PORT}")
        self.stdout.write(f"EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', False)}")
        self.stdout.write(f"EMAIL_USE_SSL: {getattr(settings, 'EMAIL_USE_SSL', False)}")
        self.stdout.write(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        self.stdout.write(f"EMAIL_HOST_PASSWORD: {'*' * 8 if settings.EMAIL_HOST_PASSWORD else 'Non configuré'}")
        self.stdout.write(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
        self.stdout.write("\n")
        
        # Si une adresse email spécifique est fournie
        if options['email']:
            email = options['email']
            self.stdout.write(f"Envoi de l'email à {email}")
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                self.stdout.write(self.style.SUCCESS(f"✅ Email envoyé avec succès à {email}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Erreur lors de l'envoi de l'email à {email}: {str(e)}"))
            return
        
        # Si un ID utilisateur spécifique est fourni
        elif options['user']:
            try:
                user = Utilisateur.objects.get(id=options['user'])
                if not user.email:
                    self.stdout.write(self.style.ERROR(f"L'utilisateur {user.get_full_name()} n'a pas d'adresse email."))
                    return
                    
                self.stdout.write(f"Envoi de l'email à {user.get_full_name()} ({user.email})")
                try:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=False,
                    )
                    self.stdout.write(self.style.SUCCESS(f"✅ Email envoyé avec succès à {user.get_full_name()}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ Erreur lors de l'envoi de l'email à {user.get_full_name()}: {str(e)}"))
                return
            except Utilisateur.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Utilisateur avec ID {options['user']} non trouvé"))
                return
        
        # Si un rôle spécifique est fourni
        elif options['role']:
            users = Utilisateur.objects.filter(
                role=options['role'],
                email__isnull=False
            ).exclude(email='')
            
            if not users.exists():
                self.stdout.write(self.style.WARNING(f"Aucun utilisateur avec le rôle {options['role']} n'a d'adresse email"))
                return
            
            self.stdout.write(f"Envoi de l'email à {users.count()} utilisateurs avec le rôle {options['role']}")
            success_count = 0
            
            for user in users:
                try:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=False,
                    )
                    success_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ Erreur lors de l'envoi de l'email à {user.get_full_name()}: {str(e)}"))
            
            self.stdout.write(self.style.SUCCESS(f"✅ Email envoyé avec succès à {success_count}/{users.count()} utilisateurs"))
        
        # Si l'option --impliques est fournie
        elif options['impliques']:
            from core.models import Course
            
            # Récupérer les utilisateurs impliqués dans des courses actives
            courses_actives = Course.objects.filter(
                Q(statut='en_attente') | Q(statut='validee') | Q(statut='en_cours')
            )
            
            utilisateurs_impliques = set()
            
            for course in courses_actives:
                if course.demandeur and course.demandeur.email:
                    utilisateurs_impliques.add(course.demandeur)
                
                if course.chauffeur and course.chauffeur.email:
                    utilisateurs_impliques.add(course.chauffeur)
                
                if course.dispatcher and course.dispatcher.email:
                    utilisateurs_impliques.add(course.dispatcher)
            
            users = list(utilisateurs_impliques)
            
            if not users:
                self.stdout.write(self.style.WARNING("Aucun utilisateur impliqué dans des courses actives n'a d'adresse email"))
                return
            
            self.stdout.write(f"Envoi de l'email à {len(users)} utilisateurs impliqués dans des courses actives")
            success_count = 0
            
            for user in users:
                try:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=False,
                    )
                    success_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ Erreur lors de l'envoi de l'email à {user.get_full_name()}: {str(e)}"))
            
            self.stdout.write(self.style.SUCCESS(f"✅ Email envoyé avec succès à {success_count}/{len(users)} utilisateurs"))
        
        # Si l'option --all est fournie
        elif options['all']:
            users = Utilisateur.objects.filter(
                email__isnull=False
            ).exclude(email='')
            
            if not users.exists():
                self.stdout.write(self.style.WARNING("Aucun utilisateur n'a d'adresse email"))
                return
            
            self.stdout.write(f"Envoi de l'email à tous les utilisateurs ({users.count()})")
            success_count = 0
            
            for user in users:
                try:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=False,
                    )
                    success_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ Erreur lors de l'envoi de l'email à {user.get_full_name()}: {str(e)}"))
            
            self.stdout.write(self.style.SUCCESS(f"✅ Email envoyé avec succès à {success_count}/{users.count()} utilisateurs"))
        
        # Si aucune option n'est fournie, tester la configuration
        else:
            self.stdout.write(f"Test de la configuration email")
            try:
                send_mail(
                    "Test de configuration email ASOFES",
                    "Ce message confirme que votre configuration SMTP fonctionne correctement.",
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.EMAIL_HOST_USER],  # Envoi à l'adresse configurée (test en boucle)
                    fail_silently=False,
                )
                self.stdout.write(self.style.SUCCESS(f"✅ Configuration email testée avec succès"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Erreur lors du test de la configuration email: {str(e)}"))
                self.stdout.write(self.style.WARNING("Consultez les instructions dans le fichier settings.py pour configurer correctement le service d'email")) 