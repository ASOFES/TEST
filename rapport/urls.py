from django.urls import path
from . import views

app_name = 'rapport'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('vehicules/', views.rapport_vehicules, name='vehicules'),
    path('missions/', views.rapport_missions, name='missions'),
    path('entretiens/', views.rapport_entretiens, name='entretiens'),
    path('carburant/', views.rapport_carburant, name='carburant'),
    path('evaluation-chauffeurs/', views.rapport_evaluation_chauffeurs, name='evaluation_chauffeurs'),
    path('demandeurs/', views.rapport_demandeurs, name='demandeurs'),
    path('vehicules-utilisation/', views.generer_rapport, {'type_rapport': 'vehicules_utilisation'}, name='vehicules_utilisation'),
    path('depenses-carburant-entretien/', views.rapport_depenses_carburant_entretien, name='depenses_carburant_entretien'),
    path('generer/<str:type_rapport>/', views.generer_rapport, name='generer_rapport'),
]
