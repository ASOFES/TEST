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
]
