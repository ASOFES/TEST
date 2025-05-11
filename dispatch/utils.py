import pandas as pd
from django.http import HttpResponse
from core.utils import render_to_pdf
from io import BytesIO

def get_demandeur_info(demandeur):
    """
    Retourne les informations complètes du demandeur sous forme de chaîne
    """
    if not demandeur:
        return 'N/A'
    
    # Essayer d'obtenir le nom complet
    full_name = demandeur.get_full_name()
    
    # Si le nom complet est vide, utiliser le nom d'utilisateur
    if not full_name.strip():
        full_name = demandeur.username
    
    # Ajouter l'email si disponible
    if demandeur.email:
        return f"{full_name} ({demandeur.email})"
    
    return full_name

def export_courses_to_excel(courses, filename='courses_export.xlsx'):
    """
    Exporte une liste de courses vers un fichier Excel
    """
    # Définir les colonnes du tableau
    columns = [
        'ID', 'Demandeur', 'Date de demande', 'Date souhaitée',
        'Point d\'embarquement', 'Destination', 'Motif', 'Nombre de passagers',
        'Statut', 'Chauffeur', 'Véhicule', 'Dispatcher',
        'Date de validation', 'Date de début', 'Date de fin'
    ]
    
    # Créer un DataFrame pandas avec les données des courses
    data = []
    for course in courses:
        try:
            course_data = {
                'ID': course.id,
                'Demandeur': get_demandeur_info(course.demandeur) if course.demandeur else 'N/A',
                'Date de demande': course.date_demande.strftime('%d/%m/%Y %H:%M') if hasattr(course, 'date_demande') and course.date_demande else 'N/A',
                'Date souhaitée': getattr(course, 'date_souhaitee', None).strftime('%d/%m/%Y %H:%M') if hasattr(course, 'date_souhaitee') and getattr(course, 'date_souhaitee') else 'N/A',
                'Point d\'embarquement': getattr(course, 'point_embarquement', 'N/A'),
                'Destination': getattr(course, 'destination', 'N/A'),
                'Motif': getattr(course, 'motif', 'N/A'),
                'Nombre de passagers': getattr(course, 'nombre_passagers', 'N/A'),
                'Statut': course.get_statut_display() if hasattr(course, 'get_statut_display') else getattr(course, 'statut', 'N/A'),
                'Chauffeur': course.chauffeur.get_full_name() if hasattr(course, 'chauffeur') and course.chauffeur else 'Non assigné',
                'Véhicule': str(course.vehicule) if hasattr(course, 'vehicule') and course.vehicule else 'Non assigné',
                'Dispatcher': course.dispatcher.get_full_name() if hasattr(course, 'dispatcher') and course.dispatcher else 'N/A',
                'Date de validation': course.date_validation.strftime('%d/%m/%Y %H:%M') if hasattr(course, 'date_validation') and course.date_validation else 'N/A',
                'Date de début': course.date_depart.strftime('%d/%m/%Y %H:%M') if hasattr(course, 'date_depart') and course.date_depart else 'N/A',
                'Date de fin': course.date_fin.strftime('%d/%m/%Y %H:%M') if hasattr(course, 'date_fin') and course.date_fin else 'N/A',
            }
            data.append(course_data)
        except Exception:
            # En cas d'erreur avec une course, créer une entrée avec des valeurs par défaut
            safe_data = {'ID': getattr(course, 'id', 'N/A')}
            for col in columns:
                if col != 'ID':
                    safe_data[col] = 'N/A'
            data.append(safe_data)
    
    df = pd.DataFrame(data)
    
    # Créer une réponse HTTP avec le fichier Excel
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Courses')
    
    # Ajuster la largeur des colonnes
    worksheet = writer.sheets['Courses']
    for i, col in enumerate(df.columns):
        column_width = max(df[col].astype(str).map(len).max(), len(col)) + 2
        worksheet.set_column(i, i, column_width)
    
    writer.close()
    output.seek(0)
    
    # Créer la réponse HTTP
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

def export_course_detail_to_excel(course, filename='course_detail_export.xlsx'):
    """
    Exporte les détails d'une course vers un fichier Excel
    """
    # Définir les attributs et les valeurs par défaut
    attributes = [
        ('ID', lambda c: c.id),
        ('Demandeur', lambda c: get_demandeur_info(c.demandeur) if c.demandeur else 'N/A'),
        ('Date de demande', lambda c: c.date_demande.strftime('%d/%m/%Y %H:%M') if c.date_demande else 'N/A'),
        ('Date souhaitée', lambda c: getattr(c, 'date_souhaitee', None).strftime('%d/%m/%Y %H:%M') 
                         if hasattr(c, 'date_souhaitee') and getattr(c, 'date_souhaitee') else 'N/A'),
        ('Point d\'embarquement', lambda c: getattr(c, 'point_embarquement', 'N/A')),
        ('Destination', lambda c: getattr(c, 'destination', 'N/A')),
        ('Motif', lambda c: getattr(c, 'motif', 'N/A')),
        ('Nombre de passagers', lambda c: getattr(c, 'nombre_passagers', 'N/A')),
        ('Statut', lambda c: c.get_statut_display() if hasattr(c, 'get_statut_display') else getattr(c, 'statut', 'N/A')),
        ('Chauffeur', lambda c: c.chauffeur.get_full_name() if hasattr(c, 'chauffeur') and c.chauffeur else 'Non assigné'),
        ('Véhicule', lambda c: str(c.vehicule) if hasattr(c, 'vehicule') and c.vehicule else 'Non assigné'),
        ('Dispatcher', lambda c: c.dispatcher.get_full_name() if hasattr(c, 'dispatcher') and c.dispatcher else 'N/A'),
        ('Date de validation', lambda c: c.date_validation.strftime('%d/%m/%Y %H:%M') 
                              if hasattr(c, 'date_validation') and c.date_validation else 'N/A'),
        ('Date de début', lambda c: c.date_depart.strftime('%d/%m/%Y %H:%M') 
                         if hasattr(c, 'date_depart') and c.date_depart else 'N/A'),
        ('Date de fin', lambda c: c.date_fin.strftime('%d/%m/%Y %H:%M') 
                       if hasattr(c, 'date_fin') and c.date_fin else 'N/A'),
        ('Commentaires', lambda c: getattr(c, 'commentaires', 'Aucun commentaire')),
    ]
    
    # Créer les listes d'attributs et de valeurs
    attr_list = [attr[0] for attr in attributes]
    try:
        value_list = [attr[1](course) for attr in attributes]
    except Exception:
        # En cas d'erreur, utiliser une approche plus sécurisée
        value_list = []
        for attr in attributes:
            try:
                value_list.append(attr[1](course))
            except Exception:
                value_list.append('N/A')
    
    # Créer un DataFrame pandas avec les données de la course
    data = {
        'Attribut': attr_list,
        'Valeur': value_list
    }
    
    df = pd.DataFrame(data)
    
    # Créer une réponse HTTP avec le fichier Excel
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Détails de la Course')
    
    # Ajuster la largeur des colonnes
    worksheet = writer.sheets['Détails de la Course']
    for i, col in enumerate(df.columns):
        column_width = max(df[col].astype(str).map(len).max(), len(col)) + 2
        worksheet.set_column(i, i, column_width)
    
    writer.close()
    output.seek(0)
    
    # Créer la réponse HTTP
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response
