from django import forms

class DemarrerMissionForm(forms.Form):
    """Formulaire pour démarrer une mission"""
    kilometrage_depart = forms.IntegerField(
        label="Kilométrage de départ",
        min_value=0,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    commentaire = forms.CharField(
        label="Commentaire",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    
    def __init__(self, *args, vehicule=None, **kwargs):
        super(DemarrerMissionForm, self).__init__(*args, **kwargs)
        self.vehicule = vehicule
    
    def clean_kilometrage_depart(self):
        """Validation du kilométrage de départ"""
        kilometrage_depart = self.cleaned_data.get('kilometrage_depart')
        
        # Vérifier que le kilométrage est positif
        if kilometrage_depart < 0:
            raise forms.ValidationError("Le kilométrage de départ ne peut pas être négatif.")
        
        return kilometrage_depart


class TerminerMissionForm(forms.Form):
    """Formulaire pour terminer une mission"""
    kilometrage_fin = forms.IntegerField(
        label="Kilométrage d'arrivée",
        min_value=0,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    commentaire = forms.CharField(
        label="Commentaire",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    
    def __init__(self, *args, kilometrage_depart=None, **kwargs):
        super(TerminerMissionForm, self).__init__(*args, **kwargs)
        self.kilometrage_depart = kilometrage_depart
    
    def clean_kilometrage_fin(self):
        """Validation du kilométrage d'arrivée"""
        kilometrage_fin = self.cleaned_data.get('kilometrage_fin')
        
        # Vérifier que le kilométrage d'arrivée est supérieur au kilométrage de départ
        if self.kilometrage_depart and kilometrage_fin < self.kilometrage_depart:
            raise forms.ValidationError(
                f"Le kilométrage d'arrivée doit être supérieur au kilométrage de départ ({self.kilometrage_depart} km)."
            )
        
        return kilometrage_fin
