from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from core.models import Utilisateur
from notifications.utils import envoyer_rappel_activation_whatsapp, envoyer_rappel_activation_groupe


class Command(BaseCommand):
    help = 'Envoie des rappels d\'activation WhatsApp aux utilisateurs'

    def add_arguments(self, parser):
        # Arguments optionnels
        parser.add_argument(
            '--user',
            type=int,
            help='ID de l\'utilisateur à qui envoyer le rappel'
        )
        
        parser.add_argument(
            '--role',
            type=str,
            help='Rôle des utilisateurs à qui envoyer le rappel (chauffeur, dispatch, demandeur, etc.)'
        )
        
        parser.add_argument(
            '--all',
            action='store_true',
            help='Envoyer à tous les utilisateurs avec un numéro de téléphone'
        )
        
        parser.add_argument(
            '--impliques',
            action='store_true',
            help='Envoyer à tous les utilisateurs impliqués dans des courses actives'
        )

    def handle(self, *args, **options):
        # Si un ID utilisateur spécifique est fourni
        if options['user']:
            try:
                user = Utilisateur.objects.get(id=options['user'])
                self.stdout.write(f"Envoi du rappel à {user.get_full_name()} ({user.role})")
                success = envoyer_rappel_activation_whatsapp(user)
                
                if success:
                    self.stdout.write(self.style.SUCCESS(f"Rappel envoyé avec succès à {user.get_full_name()}"))
                else:
                    self.stdout.write(self.style.ERROR(f"Échec de l'envoi du rappel à {user.get_full_name()}"))
                return
            except Utilisateur.DoesNotExist:
                raise CommandError(f'Utilisateur avec ID {options["user"]} non trouvé')
        
        # Si un rôle spécifique est fourni
        elif options['role']:
            users = Utilisateur.objects.filter(
                role=options['role'],
                telephone__isnull=False
            ).exclude(telephone='')
            
            if not users.exists():
                self.stdout.write(self.style.WARNING(f"Aucun utilisateur avec le rôle {options['role']} n'a de numéro de téléphone"))
                return
            
            self.stdout.write(f"Envoi du rappel à {users.count()} utilisateurs avec le rôle {options['role']}")
            results = envoyer_rappel_activation_groupe(users)
            
            success_count = sum(1 for success in results.values() if success)
            self.stdout.write(self.style.SUCCESS(f"Rappel envoyé avec succès à {success_count}/{users.count()} utilisateurs"))
        
        # Si l'option --impliques est fournie
        elif options['impliques']:
            from core.models import Course
            
            # Récupérer les utilisateurs impliqués dans des courses actives
            courses_actives = Course.objects.filter(
                Q(statut='en_attente') | Q(statut='validee') | Q(statut='en_cours')
            )
            
            utilisateurs_impliques = set()
            
            for course in courses_actives:
                if course.demandeur and course.demandeur.telephone:
                    utilisateurs_impliques.add(course.demandeur)
                
                if course.chauffeur and course.chauffeur.telephone:
                    utilisateurs_impliques.add(course.chauffeur)
                
                if course.dispatcher and course.dispatcher.telephone:
                    utilisateurs_impliques.add(course.dispatcher)
            
            users = list(utilisateurs_impliques)
            
            if not users:
                self.stdout.write(self.style.WARNING("Aucun utilisateur impliqué dans des courses actives n'a de numéro de téléphone"))
                return
            
            self.stdout.write(f"Envoi du rappel à {len(users)} utilisateurs impliqués dans des courses actives")
            results = envoyer_rappel_activation_groupe(users)
            
            success_count = sum(1 for success in results.values() if success)
            self.stdout.write(self.style.SUCCESS(f"Rappel envoyé avec succès à {success_count}/{len(users)} utilisateurs"))
        
        # Si l'option --all est fournie
        elif options['all']:
            users = Utilisateur.objects.filter(
                telephone__isnull=False
            ).exclude(telephone='')
            
            if not users.exists():
                self.stdout.write(self.style.WARNING("Aucun utilisateur n'a de numéro de téléphone"))
                return
            
            self.stdout.write(f"Envoi du rappel à tous les utilisateurs ({users.count()})")
            results = envoyer_rappel_activation_groupe(users)
            
            success_count = sum(1 for success in results.values() if success)
            self.stdout.write(self.style.SUCCESS(f"Rappel envoyé avec succès à {success_count}/{users.count()} utilisateurs"))
        
        # Si aucune option n'est fournie, afficher l'aide
        else:
            self.stdout.write(self.style.WARNING("Aucune option spécifiée. Utilisez --help pour voir les options disponibles.")) 