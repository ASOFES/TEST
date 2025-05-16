from django.contrib import admin
from .models import Message, Conversation

class MessageAdmin(admin.ModelAdmin):
    list_display = ('expediteur', 'destinataire', 'contenu_court', 'date_envoi', 'lu')
    list_filter = ('lu', 'date_envoi', 'expediteur', 'destinataire')
    search_fields = ('contenu', 'expediteur__username', 'destinataire__username')
    date_hierarchy = 'date_envoi'
    
    def contenu_court(self, obj):
        """Retourne une version tronquée du contenu"""
        if len(obj.contenu) > 50:
            return obj.contenu[:50] + '...'
        return obj.contenu
    
    contenu_court.short_description = 'Contenu'

class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_participants', 'dernier_message')
    list_filter = ('dernier_message',)
    search_fields = ('participants__username',)
    date_hierarchy = 'dernier_message'
    
    def get_participants(self, obj):
        """Retourne la liste des participants"""
        return ", ".join([str(p) for p in obj.participants.all()])
    
    get_participants.short_description = 'Participants'

admin.site.register(Message, MessageAdmin)
admin.site.register(Conversation, ConversationAdmin) 