from django.contrib import admin
from .models import Ravitaillement

class RavitaillementAdmin(admin.ModelAdmin):
    list_display = ('vehicule', 'date_ravitaillement', 'kilometrage_avant', 'kilometrage_apres', 'litres', 'cout_total', 'distance_parcourue', 'consommation_moyenne')
    list_filter = ('date_ravitaillement', 'vehicule')
    search_fields = ('vehicule__immatriculation', 'createur__username')
    date_hierarchy = 'date_ravitaillement'
    readonly_fields = ('cout_total', 'date_ravitaillement')
    fieldsets = (
        ('Informations générales', {
            'fields': ('vehicule', 'createur')
        }),
        ('Kilométrage', {
            'fields': ('kilometrage_avant', 'kilometrage_apres')
        }),
        ('Carburant', {
            'fields': ('litres', 'cout_unitaire', 'cout_total')
        }),
        ('Commentaires', {
            'fields': ('commentaires',)
        }),
    )

admin.site.register(Ravitaillement, RavitaillementAdmin)
