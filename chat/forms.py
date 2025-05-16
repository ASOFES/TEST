from django import forms
from .models import Message
from core.models import Utilisateur

class MessageForm(forms.ModelForm):
    """Formulaire pour envoyer un message"""
    class Meta:
        model = Message
        fields = ['contenu']
        widgets = {
            'contenu': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Écrivez votre message ici...'
            }),
        }
        
class ContactForm(forms.Form):
    """Formulaire pour sélectionner un contact"""
    contact = forms.ModelChoiceField(
        queryset=Utilisateur.objects.none(),
        empty_label="Sélectionner un contact",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            # Filtrer les contacts en fonction du rôle de l'utilisateur
            if user.role == 'demandeur':
                # Les demandeurs peuvent contacter les dispatchers, admins et chauffeurs
                self.fields['contact'].queryset = Utilisateur.objects.filter(
                    role__in=['dispatch', 'admin', 'chauffeur']
                ).exclude(id=user.id)
            elif user.role == 'dispatch':
                # Les dispatchers peuvent contacter tout le monde
                self.fields['contact'].queryset = Utilisateur.objects.all().exclude(id=user.id)
            elif user.role == 'admin':
                # Les admins peuvent contacter tout le monde
                self.fields['contact'].queryset = Utilisateur.objects.all().exclude(id=user.id)
            elif user.role == 'chauffeur':
                # Les chauffeurs peuvent contacter les dispatchers, admins et demandeurs
                self.fields['contact'].queryset = Utilisateur.objects.filter(
                    role__in=['dispatch', 'admin', 'demandeur']
                ).exclude(id=user.id)
            else:
                # Par défaut, limiter aux admins
                self.fields['contact'].queryset = Utilisateur.objects.filter(
                    role='admin'
                ).exclude(id=user.id) 