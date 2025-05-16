import os
import sys
import json
import django

# Configurer l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_vehicules.settings')
django.setup()

# Importer les modèles
from django.apps import apps
from django.core.serializers import serialize
from django.db.models import Model

def export_data():
    """Exporte toutes les données de la base de données au format JSON"""
    # Créer le dossier d'exportation s'il n'existe pas
    export_dir = 'db_export'
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    
    # Parcourir toutes les applications et leurs modèles
    for app_config in apps.get_app_configs():
        app_name = app_config.label
        
        # Ignorer les applications Django internes
        if app_name in ['admin', 'auth', 'contenttypes', 'sessions', 'messages', 'staticfiles']:
            continue
        
        print(f"Exportation des données de l'application {app_name}...")
        
        # Créer un fichier pour chaque modèle
        for model in app_config.get_models():
            model_name = model.__name__
            print(f"  - Exportation du modèle {model_name}")
            
            try:
                # Récupérer toutes les instances du modèle
                queryset = model.objects.all()
                
                # Sérialiser les données
                serialized_data = serialize('json', queryset, indent=4)
                
                # Écrire les données dans un fichier
                filename = os.path.join(export_dir, f"{app_name}_{model_name}.json")
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(serialized_data)
                
                print(f"    ✓ {queryset.count()} enregistrements exportés")
            
            except Exception as e:
                print(f"    ✗ Erreur lors de l'exportation: {str(e)}")
    
    print(f"\nExportation terminée. Les fichiers sont disponibles dans le dossier '{export_dir}'")

if __name__ == "__main__":
    export_data() 