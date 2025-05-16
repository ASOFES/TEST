from django.urls import path
from . import views

app_name = 'ravitaillement'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('liste/', views.liste_ravitaillements, name='liste_ravitaillements'),
    path('ajouter/', views.ajouter_ravitaillement, name='ajouter_ravitaillement'),
    path('detail/<int:ravitaillement_id>/', views.detail_ravitaillement, name='detail_ravitaillement'),
    path('modifier/<int:ravitaillement_id>/', views.modifier_ravitaillement, name='modifier_ravitaillement'),
    path('supprimer/<int:ravitaillement_id>/', views.supprimer_ravitaillement, name='supprimer_ravitaillement'),
    
    # Export routes
    path('export/pdf/', views.exporter_ravitaillements_pdf, name='exporter_ravitaillements_pdf'),
    path('export/excel/', views.exporter_ravitaillements_excel, name='exporter_ravitaillements_excel'),
    path('export/<int:ravitaillement_id>/pdf/', views.exporter_ravitaillement_pdf, name='exporter_ravitaillement_pdf'),
    path('export/<int:ravitaillement_id>/excel/', views.exporter_ravitaillement_excel, name='exporter_ravitaillement_excel'),
    
    # API routes
    path('api/vehicule/kilometrage/', views.get_vehicule_kilometrage, name='get_vehicule_kilometrage'),
]
