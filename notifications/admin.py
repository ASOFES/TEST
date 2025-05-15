from django.contrib import admin
from .models import Notification, NotificationConfig

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('destinataire', 'type_notification', 'titre', 'statut', 'date_creation', 'date_envoi')
    list_filter = ('type_notification', 'statut', 'date_creation')
    search_fields = ('destinataire__username', 'titre', 'message')
    date_hierarchy = 'date_creation'

@admin.register(NotificationConfig)
class NotificationConfigAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'sms_enabled', 'whatsapp_enabled', 'email_enabled')
    list_filter = ('sms_enabled', 'whatsapp_enabled', 'email_enabled')
    search_fields = ('utilisateur__username',)
