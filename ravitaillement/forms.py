from django import forms
from .models import Ravitaillement
from core.models import Vehicule

class RavitaillementForm(forms.ModelForm):
    """Formulaire pour la création et modification de ravitaillements"""
    
    class Meta:
        model = Ravitaillement
        fields = ['vehicule', 'nom_station', 'kilometrage_avant', 'kilometrage_apres', 'litres', 'cout_unitaire', 'commentaires', 'image']
        widgets = {
            'vehicule': forms.Select(attrs={'class': 'form-select'}),
            'nom_station': forms.TextInput(attrs={'class': 'form-control'}),
            'kilometrage_avant': forms.NumberInput(attrs={'class': 'form-control'}),
            'kilometrage_apres': forms.NumberInput(attrs={'class': 'form-control'}),
            'litres': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'cout_unitaire': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'commentaires': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.createur = kwargs.pop('createur', None)
        super().__init__(*args, **kwargs)
        
        # Filtrer les véhicules actifs uniquement
        self.fields['vehicule'].queryset = Vehicule.objects.all().order_by('immatriculation')
        
        # Ajouter des labels plus descriptifs
        self.fields['vehicule'].label = "Véhicule"
        self.fields['nom_station'].label = "Nom de la station"
        # Le champ date_ravitaillement est automatiquement défini dans le modèle
        self.fields['kilometrage_avant'].label = "Kilométrage avant"
        self.fields['kilometrage_apres'].label = "Kilométrage après"
        self.fields['litres'].label = "Quantité (litres)"
        self.fields['cout_unitaire'].label = "Prix unitaire ($/L)"
        self.fields['commentaires'].label = "Commentaires additionnels"
        self.fields['image'].label = "Photo du reçu (optionnel)"
        
        # Nous n'utilisons pas de champ calculé dans le formulaire pour éviter les erreurs
        # Le calcul sera fait côté JavaScript dans le template
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.createur:
            instance.createur = self.createur
        if commit:
            instance.save()
        return instance
