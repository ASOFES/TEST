from django import forms
from django.utils import timezone
from .models import Entretien
from core.models import Vehicule

class EntretienForm(forms.ModelForm):
    """Formulaire pour la création et modification d'entretiens"""
    date_entretien = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        initial=timezone.now().date
    )
    
    class Meta:
        model = Entretien
        fields = ['vehicule', 'garage', 'date_entretien', 'statut', 'motif', 'cout', 'commentaires']
        widgets = {
            'vehicule': forms.Select(attrs={'class': 'form-select'}),
            'garage': forms.TextInput(attrs={'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'motif': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cout': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'commentaires': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.createur = kwargs.pop('createur', None)
        super().__init__(*args, **kwargs)
        
        # Filtrer les véhicules actifs uniquement
        self.fields['vehicule'].queryset = Vehicule.objects.all().order_by('immatriculation')
        
        # Ajouter des labels plus descriptifs
        self.fields['vehicule'].label = "Véhicule"
        self.fields['garage'].label = "Garage / Prestataire"
        self.fields['date_entretien'].label = "Date de l'entretien"
        self.fields['statut'].label = "Statut"
        self.fields['motif'].label = "Motif de l'entretien"
        self.fields['cout'].label = "Coût (€)"
        self.fields['commentaires'].label = "Commentaires additionnels"
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.createur:
            instance.createur = self.createur
        if commit:
            instance.save()
        return instance
