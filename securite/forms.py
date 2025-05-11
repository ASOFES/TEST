from django import forms
from .models import CheckListSecurite
from core.models import Vehicule

class ChecklistSecuriteForm(forms.ModelForm):
    """Formulaire pour la création d'une checklist de sécurité"""
    
    # Le champ type_check a été supprimé dans la migration 0002_update_checklistsecurite.py
    
    lieu_controle = forms.CharField(
        label="Lieu du contrôle",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    kilometrage = forms.IntegerField(
        label="Kilométrage actuel",
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    vehicule = forms.ModelChoiceField(
        label="Véhicule",
        queryset=Vehicule.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # Éléments de la check-list avec des choix
    phares_avant = forms.ChoiceField(
        label="Phares avant",
        choices=[
            ('ok', 'OK'),
            ('defectueux', 'Défectueux')
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='ok'
    )
    
    phares_arriere = forms.ChoiceField(
        label="Phares arrière",
        choices=[
            ('ok', 'OK'),
            ('defectueux', 'Défectueux')
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='ok'
    )
    
    clignotants = forms.ChoiceField(
        label="Clignotants",
        choices=[
            ('ok', 'OK'),
            ('defectueux', 'Défectueux')
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='ok'
    )
    
    etat_pneus = forms.ChoiceField(
        label="État des pneus",
        choices=[
            ('ok', 'OK'),
            ('usure', 'Usure'),
            ('critique', 'Critique')
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='ok'
    )
    
    carrosserie = forms.ChoiceField(
        label="Carrosserie",
        choices=[
            ('ok', 'OK'),
            ('rayures', 'Rayures mineures'),
            ('dommages', 'Dommages importants')
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='ok'
    )
    
    tableau_bord = forms.ChoiceField(
        label="Tableau de bord",
        choices=[
            ('ok', 'OK'),
            ('voyants', 'Voyants allumés')
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='ok'
    )
    
    freins = forms.ChoiceField(
        label="Freins",
        choices=[
            ('ok', 'OK'),
            ('usure', 'Usure'),
            ('defectueux', 'Défectueux')
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='ok'
    )
    
    ceintures = forms.ChoiceField(
        label="Ceintures de sécurité",
        choices=[
            ('ok', 'OK'),
            ('defectueuses', 'Défectueuses')
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='ok'
    )
    
    proprete = forms.ChoiceField(
        label="Propreté",
        choices=[
            ('ok', 'OK'),
            ('sale', 'Sale')
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='ok'
    )
    
    carte_grise = forms.ChoiceField(
        label="Carte grise",
        choices=[
            ('present', 'Présente'),
            ('absent', 'Absente')
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='present'
    )
    
    assurance = forms.ChoiceField(
        label="Assurance",
        choices=[
            ('present', 'Présente'),
            ('absent', 'Absente')
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='present'
    )
    
    triangle = forms.ChoiceField(
        label="Triangle de signalisation",
        choices=[
            ('present', 'Présent'),
            ('absent', 'Absent')
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='present'
    )
    
    logos = forms.ChoiceField(
        label="Logos",
        choices=[
            ('present', 'Présents'),
            ('absent', 'Absents')
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='present'
    )
    
    commentaires = forms.CharField(
        label="Commentaires",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
    )
    
    class Meta:
        model = CheckListSecurite
        fields = ['vehicule', 'lieu_controle', 'kilometrage', 'type_check', 'phares_avant', 'phares_arriere', 
                 'clignotants', 'etat_pneus', 'carrosserie', 'tableau_bord', 'freins', 
                 'ceintures', 'proprete', 'carte_grise', 'assurance', 'triangle', 'logos', 'commentaires']
    
    def clean_kilometrage(self):
        """Validation du kilométrage"""
        kilometrage = self.cleaned_data.get('kilometrage')
        
        # Vérification simple que le kilométrage est positif
        if kilometrage < 0:
            raise forms.ValidationError("Le kilométrage ne peut pas être négatif.")
        
        return kilometrage
    
    def save(self, commit=True, controleur=None):
        """Sauvegarde de la checklist"""
        instance = super().save(commit=False)
        
        # Définir le contrôleur
        if controleur:
            instance.controleur = controleur
        
        # Déterminer le statut en fonction des réponses
        # Si tous les éléments sont cochés, le véhicule est conforme
        elements = [
            self.cleaned_data.get('parebrise_avant'),
            self.cleaned_data.get('parebrise_arriere'),
            self.cleaned_data.get('retroviseur_gauche'),
            self.cleaned_data.get('retroviseur_droit'),
            self.cleaned_data.get('clignotant'),
            self.cleaned_data.get('feu_arriere_gauche'),
            self.cleaned_data.get('feu_arriere_droit'),
            self.cleaned_data.get('feu_position_gauche'),
            self.cleaned_data.get('feu_position_droit')
        ]
        
        # Compter le nombre d'éléments cochés
        checked_count = sum(1 for element in elements if element)
        
        # Définir le statut en fonction du nombre d'éléments cochés
        if checked_count == len(elements):
            instance.statut = 'conforme'
        elif checked_count >= len(elements) * 0.7:  # Au moins 70% des éléments sont OK
            instance.statut = 'anomalie_mineure'
        else:
            instance.statut = 'non_conforme'
        
        if commit:
            instance.save()
        
        return instance
