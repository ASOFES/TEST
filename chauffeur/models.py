from django.db import models
from core.models import Utilisateur, Course, Vehicule, ActionTraceur

class HistoriqueChauffeur(models.Model):
    """Modèle pour suivre l'historique des actions du chauffeur"""
    chauffeur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='historique_chauffeur')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='historique_chauffeur')
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name='historique_chauffeur')
    date_action = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=50)  # 'depart', 'arrivee'
    kilometrage = models.PositiveIntegerField()
    commentaire = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.action} par {self.chauffeur.username} - Course {self.course.id}"
    
    def save(self, *args, **kwargs):
        # Créer une entrée dans le traceur d'actions
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            ActionTraceur.objects.create(
                utilisateur=self.chauffeur,
                action=f"Chauffeur: {self.action}",
                details=f"Course {self.course.id}, Véhicule: {self.vehicule.immatriculation}, Kilométrage: {self.kilometrage}"
            )

class DistanceJournaliere(models.Model):
    """Modèle pour suivre la distance journalière parcourue par chauffeur"""
    chauffeur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='distances_journalieres')
    date = models.DateField()
    distance_totale = models.PositiveIntegerField(default=0)
    nombre_courses = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ('chauffeur', 'date')
    
    def __str__(self):
        return f"{self.chauffeur.username} - {self.date} - {self.distance_totale} km"
    
    @classmethod
    def mettre_a_jour_distance(cls, chauffeur, date, distance):
        """Met à jour la distance journalière pour un chauffeur"""
        obj, created = cls.objects.get_or_create(
            chauffeur=chauffeur,
            date=date,
            defaults={'distance_totale': distance, 'nombre_courses': 1}
        )
        
        if not created:
            obj.distance_totale += distance
            obj.nombre_courses += 1
            obj.save()
        
        return obj
