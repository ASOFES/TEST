from django.core.management.base import BaseCommand
from django.conf import settings
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import smtplib
from email.mime.text import MIMEText
import os
import sys

class Command(BaseCommand):
    help = 'Vérifie l\'état des services de notification (SMS, WhatsApp, Email)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--detail',
            action='store_true',
            help='Affiche des informations détaillées sur chaque service'
        )
        
    def handle(self, *args, **options):
        detail = options['detail']
        
        self.stdout.write(self.style.HTTP_INFO("=== VÉRIFICATION DES SERVICES DE NOTIFICATION ==="))
        
        # Vérification des services
        twilio_status = self.verifier_twilio(detail)
        email_status = self.verifier_email(detail)
        
        # Affichage du résumé
        self.stdout.write("\n=== RÉSUMÉ ===")
        
        if twilio_status['sms'] and twilio_status['whatsapp'] and email_status:
            self.stdout.write(self.style.SUCCESS("✅ Tous les services de notification sont opérationnels"))
        else:
            self.stdout.write(self.style.ERROR("❌ Certains services de notification ne sont pas opérationnels"))
        
        self.stdout.write(f"SMS: {'✅' if twilio_status['sms'] else '❌'}")
        self.stdout.write(f"WhatsApp: {'✅' if twilio_status['whatsapp'] else '❌'}")
        self.stdout.write(f"Email: {'✅' if email_status else '❌'}")
    
    def verifier_twilio(self, detail=False):
        """Vérifie si les services Twilio (SMS et WhatsApp) sont correctement configurés et opérationnels"""
        self.stdout.write("\n=== VÉRIFICATION TWILIO (SMS ET WHATSAPP) ===")
        
        # Vérification de la configuration
        twilio_configured = all([
            getattr(settings, 'TWILIO_ACCOUNT_SID', None),
            getattr(settings, 'TWILIO_AUTH_TOKEN', None),
            getattr(settings, 'TWILIO_PHONE_NUMBER', None),
            getattr(settings, 'TWILIO_WHATSAPP_NUMBER', None)
        ])
        
        if not twilio_configured:
            self.stdout.write(self.style.ERROR("❌ Configuration Twilio incomplète"))
            if detail:
                self.stdout.write(f"  TWILIO_ACCOUNT_SID: {'✅' if getattr(settings, 'TWILIO_ACCOUNT_SID', None) else '❌'}")
                self.stdout.write(f"  TWILIO_AUTH_TOKEN: {'✅' if getattr(settings, 'TWILIO_AUTH_TOKEN', None) else '❌'}")
                self.stdout.write(f"  TWILIO_PHONE_NUMBER: {'✅' if getattr(settings, 'TWILIO_PHONE_NUMBER', None) else '❌'}")
                self.stdout.write(f"  TWILIO_WHATSAPP_NUMBER: {'✅' if getattr(settings, 'TWILIO_WHATSAPP_NUMBER', None) else '❌'}")
            return {'sms': False, 'whatsapp': False}
        
        self.stdout.write(self.style.SUCCESS("✅ Configuration Twilio complète"))
        if detail:
            self.stdout.write(f"  TWILIO_ACCOUNT_SID: {settings.TWILIO_ACCOUNT_SID[:5]}...{settings.TWILIO_ACCOUNT_SID[-5:]}")
            self.stdout.write(f"  TWILIO_AUTH_TOKEN: {settings.TWILIO_AUTH_TOKEN[:2]}...{settings.TWILIO_AUTH_TOKEN[-2:]}")
            self.stdout.write(f"  TWILIO_PHONE_NUMBER: {settings.TWILIO_PHONE_NUMBER}")
            self.stdout.write(f"  TWILIO_WHATSAPP_NUMBER: {settings.TWILIO_WHATSAPP_NUMBER}")
        
        # Test de connexion à l'API Twilio
        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            account = client.api.accounts(settings.TWILIO_ACCOUNT_SID).fetch()
            self.stdout.write(self.style.SUCCESS(f"✅ Connexion à l'API Twilio réussie (compte: {account.friendly_name})"))
            
            # Vérification du solde du compte
            if detail:
                try:
                    balance = client.api.accounts(settings.TWILIO_ACCOUNT_SID).balance.fetch()
                    self.stdout.write(f"  Solde du compte: {balance.balance} {balance.currency}")
                    if float(balance.balance) < 10:
                        self.stdout.write(self.style.WARNING(f"  ⚠️ Solde du compte faible ({balance.balance} {balance.currency})"))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"  ⚠️ Impossible de vérifier le solde du compte: {str(e)}"))
            
            # Vérification du numéro SMS
            sms_valid = False
            try:
                incoming_phone_numbers = client.incoming_phone_numbers.list(phone_number=settings.TWILIO_PHONE_NUMBER)
                if incoming_phone_numbers:
                    sms_valid = True
                    self.stdout.write(self.style.SUCCESS(f"✅ Numéro SMS vérifié"))
                    if detail:
                        self.stdout.write(f"  Capacités: {', '.join(incoming_phone_numbers[0].capabilities.keys())}")
                else:
                    self.stdout.write(self.style.ERROR(f"❌ Numéro SMS {settings.TWILIO_PHONE_NUMBER} non trouvé dans le compte"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Erreur lors de la vérification du numéro SMS: {str(e)}"))
            
            # Vérification du numéro WhatsApp
            whatsapp_valid = False
            try:
                whatsapp_number = settings.TWILIO_WHATSAPP_NUMBER
                # Il n'y a pas de vérification directe pour WhatsApp, on suppose que c'est valide si le numéro existe
                incoming_phone_numbers = client.incoming_phone_numbers.list(phone_number=whatsapp_number)
                if incoming_phone_numbers:
                    whatsapp_valid = True
                    self.stdout.write(self.style.SUCCESS(f"✅ Numéro WhatsApp vérifié"))
                else:
                    self.stdout.write(self.style.WARNING(f"⚠️ Numéro WhatsApp {whatsapp_number} non trouvé dans le compte"))
                    # WhatsApp peut fonctionner même si le numéro n'est pas dans la liste des numéros entrants
                    whatsapp_valid = True
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Erreur lors de la vérification du numéro WhatsApp: {str(e)}"))
            
            return {'sms': sms_valid, 'whatsapp': whatsapp_valid}
            
        except TwilioRestException as e:
            self.stdout.write(self.style.ERROR(f"❌ Erreur d'authentification Twilio: {e.msg}"))
            return {'sms': False, 'whatsapp': False}
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erreur de connexion à l'API Twilio: {str(e)}"))
            return {'sms': False, 'whatsapp': False}
    
    def verifier_email(self, detail=False):
        """Vérifie si le service d'email est correctement configuré et opérationnel"""
        self.stdout.write("\n=== VÉRIFICATION EMAIL ===")
        
        # Vérification de la configuration
        email_configured = all([
            getattr(settings, 'EMAIL_HOST', None),
            getattr(settings, 'EMAIL_PORT', None),
            getattr(settings, 'EMAIL_HOST_USER', None),
            getattr(settings, 'EMAIL_HOST_PASSWORD', None),
            getattr(settings, 'DEFAULT_FROM_EMAIL', None)
        ])
        
        if not email_configured:
            self.stdout.write(self.style.ERROR("❌ Configuration Email incomplète"))
            if detail:
                self.stdout.write(f"  EMAIL_HOST: {'✅' if getattr(settings, 'EMAIL_HOST', None) else '❌'}")
                self.stdout.write(f"  EMAIL_PORT: {'✅' if getattr(settings, 'EMAIL_PORT', None) else '❌'}")
                self.stdout.write(f"  EMAIL_HOST_USER: {'✅' if getattr(settings, 'EMAIL_HOST_USER', None) else '❌'}")
                self.stdout.write(f"  EMAIL_HOST_PASSWORD: {'✅' if getattr(settings, 'EMAIL_HOST_PASSWORD', None) else '❌'}")
                self.stdout.write(f"  DEFAULT_FROM_EMAIL: {'✅' if getattr(settings, 'DEFAULT_FROM_EMAIL', None) else '❌'}")
            return False
        
        self.stdout.write(self.style.SUCCESS("✅ Configuration Email complète"))
        if detail:
            self.stdout.write(f"  EMAIL_HOST: {settings.EMAIL_HOST}")
            self.stdout.write(f"  EMAIL_PORT: {settings.EMAIL_PORT}")
            self.stdout.write(f"  EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
            self.stdout.write(f"  EMAIL_HOST_PASSWORD: {'*' * 8}")  # Ne pas afficher le mot de passe
            self.stdout.write(f"  DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
        
        # Test de connexion au serveur SMTP
        try:
            use_tls = getattr(settings, 'EMAIL_USE_TLS', False)
            use_ssl = getattr(settings, 'EMAIL_USE_SSL', False)
            
            if use_ssl:
                server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
            else:
                server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
                
            if use_tls:
                server.starttls()
            
            self.stdout.write(self.style.SUCCESS(f"✅ Connexion au serveur SMTP réussie"))
            
            # Test d'authentification
            try:
                server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                self.stdout.write(self.style.SUCCESS(f"✅ Authentification SMTP réussie"))
                
                # Test d'envoi d'email (si demandé en détail)
                if detail:
                    self.stdout.write("  ℹ️ Un test d'envoi complet nécessite l'envoi d'un email réel (non effectué)")
                
                server.quit()
                return True
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Authentification SMTP échouée: {str(e)}"))
                server.quit()
                return False
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Connexion au serveur SMTP échouée: {str(e)}"))
            return False 