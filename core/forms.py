from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Utilisateur

class UtilisateurCreationForm(UserCreationForm):
    """Formulaire de création d'utilisateur personnalisé"""
    class Meta:
        model = Utilisateur
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'telephone', 'adresse', 'photo')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre les champs obligatoires plus visibles
        for field_name in ['username', 'email', 'role', 'password1', 'password2']:
            self.fields[field_name].widget.attrs['class'] = 'form-control is-required'
        
        # Ajouter des classes Bootstrap aux autres champs
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
                
        # S'assurer que les champs de mot de passe sont bien présents
        if 'password1' not in self.fields or 'password2' not in self.fields:
            raise ValueError("Les champs de mot de passe sont manquants dans le formulaire")

class UtilisateurChangeForm(UserChangeForm):
    """Formulaire de modification d'utilisateur personnalisé"""
    password = None  # Supprimer le champ de mot de passe du formulaire de modification
    
    class Meta:
        model = Utilisateur
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'telephone', 'adresse', 'photo', 'is_active')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajouter des classes Bootstrap à tous les champs
        for _, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
