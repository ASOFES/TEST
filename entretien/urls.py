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
]
