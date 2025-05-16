from django.db import models
from django.utils import timezone
from core.models import Utilisateur

class Message(models.Model):
    """Modèle pour les messages de chat entre utilisateurs"""
    expediteur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='messages_envoyes')
    destinataire = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='messages_recus')
    contenu = models.TextField()
    date_envoi = models.DateTimeField(default=timezone.now)
    lu = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['date_envoi']
        
    def __str__(self):
        return f"Message de {self.expediteur} à {self.destinataire} ({self.date_envoi.strftime('%d/%m/%Y %H:%M')})"
        
    def marquer_comme_lu(self):
        """Marque le message comme lu"""
        self.lu = True
        self.save()
        
class Conversation(models.Model):
    """Modèle pour représenter une conversation entre deux utilisateurs"""
    participants = models.ManyToManyField(Utilisateur, related_name='conversations')
    dernier_message = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-dernier_message']
        
    def __str__(self):
        return f"Conversation {self.id} - {', '.join([str(p) for p in self.participants.all()])}"
        
    def get_messages(self):
        """Récupère tous les messages de la conversation"""
        participants = self.participants.all()
        if participants.count() != 2:
            return Message.objects.none()
            
        user1, user2 = participants[0], participants[1]
        return Message.objects.filter(
            (models.Q(expediteur=user1) & models.Q(destinataire=user2)) |
            (models.Q(expediteur=user2) & models.Q(destinataire=user1))
        ).order_by('date_envoi')
        
    def get_unread_count(self, user):
        """Récupère le nombre de messages non lus pour un utilisateur"""
        participants = self.participants.all()
        if participants.count() != 2 or user not in participants:
            return 0
            
        other_user = participants.exclude(id=user.id).first()
        return Message.objects.filter(
            expediteur=other_user,
            destinataire=user,
            lu=False
        ).count()
        
    @classmethod
    def get_or_create_conversation(cls, user1, user2):
        """Récupère ou crée une conversation entre deux utilisateurs"""
        # Rechercher une conversation existante
        conversations = Conversation.objects.filter(participants=user1).filter(participants=user2)
        
        if conversations.exists():
            return conversations.first()
        else:
            # Créer une nouvelle conversation
            conversation = Conversation.objects.create()
            conversation.participants.add(user1, user2)
            return conversation 