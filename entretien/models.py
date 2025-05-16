from django.db import models
from core.models import Utilisateur, Vehicule, ActionTraceur

def piece_justificative_path(instance, filename):
    """Définit le chemin où seront stockées les pièces justificatives"""
    # Format: entretien/vehicule_id/YYYYMMDD_filename
    return f'entretien/{instance.vehicule.id}/{instance.date_entretien.strftime("%Y%m%d")}_{filename}'

class Entretien(models.Model):
    """Modèle pour les entretiens de véhicules"""
    STATUS_CHOICES = (
        ('planifie', 'Planifié'),
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
        ('annule', 'Annulé'),
    )
    
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name='entretiens')
    garage = models.CharField(max_length=255)
    date_entretien = models.DateField()
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planifie')
    motif = models.TextField()
    cout = models.DecimalField(max_digits=10, decimal_places=2)
    kilometrage = models.PositiveIntegerField(default=0, help_text="Kilométrage du véhicule au moment de l'entretien")
    piece_justificative = models.FileField(upload_to=piece_justificative_path, blank=True, null=True, 
                                          help_text="Facture, reçu ou autre document justificatif (PDF, JPG, PNG)")
    createur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='entretiens_crees')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    commentaires = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Entretien {self.vehicule.immatriculation} - {self.date_entretien} - {self.get_statut_display()}"
    
    def save(self, *args, **kwargs):
        # Créer une entrée dans le traceur d'actions
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            ActionTraceur.objects.create(
                utilisateur=self.createur,
                action="Création d'entretien",
                details=f"Véhicule: {self.vehicule.immatriculation}, Date: {self.date_entretien}, Coût: {self.cout}"
            )
        else:
            ActionTraceur.objects.create(
                utilisateur=self.createur,
                action="Modification d'entretien",
                details=f"Véhicule: {self.vehicule.immatriculation}, Date: {self.date_entretien}, Coût: {self.cout}"
            )
    
    @classmethod
    def cout_total_par_vehicule(cls, vehicule):
        """Retourne le coût total des entretiens pour un véhicule"""
        from django.db.models import Sum
        return cls.objects.filter(vehicule=vehicule, statut='termine').aggregate(Sum('cout'))['cout__sum'] or 0
    
    @classmethod
    def cout_total_par_periode(cls, date_debut, date_fin):
        """Retourne le coût total des entretiens pour une période donnée"""
        from django.db.models import Sum
        return cls.objects.filter(date_entretien__range=[date_debut, date_fin], statut='termine').aggregate(Sum('cout'))['cout__sum'] or 0
