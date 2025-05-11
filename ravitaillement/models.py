from django.db import models
from core.models import Utilisateur, Vehicule, ActionTraceur

class Ravitaillement(models.Model):
    """Modèle pour les ravitaillements de véhicules"""
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name='ravitaillements')
    date_ravitaillement = models.DateTimeField(auto_now_add=True)  # On garde auto_now_add pour simplifier
    kilometrage_avant = models.PositiveIntegerField(default=0)
    kilometrage_apres = models.PositiveIntegerField(default=0)
    litres = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    cout_unitaire = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    cout_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    createur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='ravitaillements_crees')
    commentaires = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Ravitaillement {self.vehicule.immatriculation} - {self.date_ravitaillement}"
    
    def save(self, *args, **kwargs):
        # Calcul automatique du coût total
        self.cout_total = self.litres * self.cout_unitaire
        
        # Créer une entrée dans le traceur d'actions
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            ActionTraceur.objects.create(
                utilisateur=self.createur,
                action="Ravitaillement",
                details=f"Véhicule: {self.vehicule.immatriculation}, Litres: {self.litres}, Coût: {self.cout_total}"
            )
    
    @property
    def distance_parcourue(self):
        """Calcule la distance parcourue entre deux ravitaillements"""
        return self.kilometrage_apres - self.kilometrage_avant
    
    @property
    def consommation_moyenne(self):
        """Calcule la consommation moyenne en litres/100km"""
        if self.distance_parcourue > 0:
            return (self.litres * 100) / self.distance_parcourue
        return 0
    
    @classmethod
    def cout_total_par_vehicule(cls, vehicule):
        """Retourne le coût total des ravitaillements pour un véhicule"""
        from django.db.models import Sum
        return cls.objects.filter(vehicule=vehicule).aggregate(Sum('cout_total'))['cout_total__sum'] or 0
    
    @classmethod
    def cout_total_par_periode(cls, date_debut, date_fin):
        """Retourne le coût total des ravitaillements pour une période donnée"""
        from django.db.models import Sum
        return cls.objects.filter(date_ravitaillement__range=[date_debut, date_fin]).aggregate(Sum('cout_total'))['cout_total__sum'] or 0
