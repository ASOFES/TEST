from django.urls import path
from . import views

app_name = 'entretien'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('liste/', views.liste_entretiens, name='liste_entretiens'),
    path('ajouter/', views.ajouter_entretien, name='ajouter_entretien'),
    path('detail/<int:entretien_id>/', views.detail_entretien, name='detail_entretien'),
    path('modifier/<int:entretien_id>/', views.modifier_entretien, name='modifier_entretien'),
    path('supprimer/<int:entretien_id>/', views.supprimer_entretien, name='supprimer_entretien'),
    
    # Export routes
    path('export/pdf/', views.exporter_entretiens_pdf, name='exporter_entretiens_pdf'),
    path('export/excel/', views.exporter_entretiens_excel, name='exporter_entretiens_excel'),
    path('export/<int:entretien_id>/pdf/', views.exporter_entretien_pdf, name='exporter_entretien_pdf'),
    path('export/<int:entretien_id>/excel/', views.exporter_entretien_excel, name='exporter_entretien_excel'),
    
    # API routes
    path('api/vehicule/kilometrage/', views.get_vehicule_kilometrage, name='get_vehicule_kilometrage'),
]
