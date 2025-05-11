from django.db import models
from django.utils import timezone
from core.models import Utilisateur, Vehicule, ActionTraceur

class CheckListSecurite(models.Model):
    """Modèle pour la check-list de sécurité avant et après course"""
    # Le champ type_check a été supprimé dans la migration 0002_update_checklistsecurite.py
    
    STATUT_CHOICES = (
        ('conforme', 'Conforme'),
        ('anomalie_mineure', 'Anomalie mineure'),
        ('non_conforme', 'Non conforme'),
    )
    
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name='check_lists')
    controleur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='check_lists_effectuees')
    # Champs ajoutés dans la migration 0002
    date_controle = models.DateTimeField(default=timezone.now)
    lieu_controle = models.CharField(max_length=100)
    
    # Nouveaux champs ajoutés dans la migration 0002
    # Statut global de la checklist
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='conforme')
    
    # Éléments de la check-list avec des choix
    phares_avant = models.CharField(max_length=20, choices=[
        ('ok', 'OK'), 
        ('defectueux', 'Défectueux')
    ], default='ok')
    
    phares_arriere = models.CharField(max_length=20, choices=[
        ('ok', 'OK'), 
        ('defectueux', 'Défectueux')
    ], default='ok')
    
    clignotants = models.CharField(max_length=20, choices=[
        ('ok', 'OK'), 
        ('defectueux', 'Défectueux')
    ], default='ok')
    
    etat_pneus = models.CharField(max_length=20, choices=[
        ('ok', 'OK'), 
        ('usure', 'Usure'), 
        ('critique', 'Critique')
    ], default='ok')
    
    carrosserie = models.CharField(max_length=20, choices=[
        ('ok', 'OK'), 
        ('rayures', 'Rayures mineures'), 
        ('dommages', 'Dommages importants')
    ], default='ok')
    
    tableau_bord = models.CharField(max_length=20, choices=[
        ('ok', 'OK'), 
        ('voyants', 'Voyants allumés')
    ], default='ok')
    
    freins = models.CharField(max_length=20, choices=[
        ('ok', 'OK'), 
        ('usure', 'Usure'), 
        ('defectueux', 'Défectueux')
    ], default='ok')
    
    ceintures = models.CharField(max_length=20, choices=[
        ('ok', 'OK'), 
        ('defectueuses', 'Défectueuses')
    ], default='ok')
    
    proprete = models.CharField(max_length=20, choices=[
        ('ok', 'OK'), 
        ('sale', 'Sale')
    ], default='ok')
    
    carte_grise = models.CharField(max_length=20, choices=[
        ('present', 'Présente'), 
        ('absent', 'Absente')
    ], default='present')
    
    assurance = models.CharField(max_length=20, choices=[
        ('present', 'Présente'), 
        ('absent', 'Absente')
    ], default='present')
    
    triangle = models.CharField(max_length=20, choices=[
        ('present', 'Présent'), 
        ('absent', 'Absent')
    ], default='present')
    
    logos = models.CharField(max_length=20, choices=[
        ('present', 'Présents'), 
        ('absent', 'Absents')
    ], default='present')
    
    type_check = models.CharField(
    max_length=10,
    choices=[('depart', 'Avant course'), ('retour', 'Après course')],
    default='depart',
    verbose_name='Type de check-list'
)

# Kilométrage
    kilometrage = models.PositiveIntegerField()
    
    # Commentaires
    commentaires = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Check-list {self.vehicule.immatriculation} - {self.date_controle}"
    
    def save(self, *args, **kwargs):
        # Créer une entrée dans le traceur d'actions
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            action = f"Check-list effectuée pour le véhicule {self.vehicule.immatriculation}"
            ActionTraceur.objects.create(
                utilisateur=self.controleur,
                action=action,
                details=f"Kilométrage: {self.kilometrage}"
            )
            
            # Le modèle Vehicule n'a pas d'attribut kilometrage_actuel, donc nous ne mettons pas à jour le kilométrage
            # Le kilométrage est stocké uniquement dans la checklist
