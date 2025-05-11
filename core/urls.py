from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # Gestion des utilisateurs
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:pk>/password-reset/', views.user_password_reset, name='user_password_reset'),
    path('users/<int:pk>/toggle-active/', views.user_toggle_active, name='user_toggle_active'),
    
    # Gestion des véhicules
    path('vehicules/', views.vehicule_list, name='vehicule_list'),
    path('vehicules/create/', views.vehicule_create, name='vehicule_create'),
    path('vehicules/<int:pk>/', views.vehicule_detail, name='vehicule_detail'),
    path('vehicules/<int:pk>/edit/', views.vehicule_edit, name='vehicule_edit'),
    path('vehicules/<int:pk>/delete/', views.vehicule_delete, name='vehicule_delete'),
    
    # Export PDF des véhicules
    path('vehicules/export/pdf/', views.vehicule_list_pdf, name='vehicule_list_pdf'),
    path('vehicules/<int:pk>/export/pdf/', views.vehicule_detail_pdf, name='vehicule_detail_pdf'),
]
