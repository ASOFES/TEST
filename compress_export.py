import os
import zipfile
from datetime import datetime

def compress_export_files():
    """Compresse les fichiers d'exportation dans une archive ZIP"""
    # Dossier contenant les fichiers d'exportation
    export_dir = 'db_export'
    
    # Vérifier que le dossier existe
    if not os.path.exists(export_dir):
        print(f"Le dossier {export_dir} n'existe pas.")
        return
    
    # Nom du fichier ZIP avec la date et l'heure actuelles
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_filename = f"database_export_{timestamp}.zip"
    
    # Créer l'archive ZIP
    print(f"Création de l'archive {zip_filename}...")
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Parcourir tous les fichiers du dossier d'exportation
        for root, dirs, files in os.walk(export_dir):
            for file in files:
                # Chemin complet du fichier
                file_path = os.path.join(root, file)
                # Chemin relatif pour l'archive
                arcname = os.path.relpath(file_path, os.path.dirname(export_dir))
                # Ajouter le fichier à l'archive
                print(f"  Ajout du fichier {file}")
                zipf.write(file_path, arcname)
    
    print(f"\nCompression terminée. L'archive est disponible sous le nom '{zip_filename}'")

if __name__ == "__main__":
    compress_export_files() 