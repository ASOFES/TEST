import os
import base64
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders
import io
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import xlsxwriter


def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those resources
    """
    # Si l'URI est un chemin absolu, le retourner directement
    if os.path.isabs(uri):
        return uri
        
    # Essayer de trouver le fichier via le système de fichiers statiques de Django
    result = finders.find(uri)
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
        result = list(os.path.realpath(path) for path in result)
        path = result[0]
        return path
        
    # Gérer les chemins relatifs
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Vérifier si c'est un chemin statique
    if uri.startswith('static/'):
        path = os.path.join(base_dir, uri)
        if os.path.isfile(path):
            return path
            
    # Vérifier si c'est un chemin média
    if uri.startswith('media/'):
        path = os.path.join(base_dir, uri)
        if os.path.isfile(path):
            return path
    
    # Dernier recours: essayer de trouver le fichier dans le répertoire statique
    path = os.path.join(base_dir, 'static', uri)
    if os.path.isfile(path):
        return path
        
    # Si tout échoue, retourner l'URI tel quel
    return uri


def render_to_pdf(template_src, context_dict={}):
    """
    Génère un PDF à partir d'un template HTML et d'un dictionnaire de contexte
    """
    # Ajouter le chemin absolu du logo MAMO
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logo_path = os.path.abspath(os.path.join(base_dir, 'static', 'img', 'logo_mamo.png'))
    
    # Convertir le logo en data URI pour éviter les problèmes de chemin
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            data_uri = f"data:image/png;base64,{encoded_string}"
            context_dict['logo_data_uri'] = data_uri
    
    template = get_template(template_src)
    html = template.render(context_dict)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="export.pdf"'
    
    # create a pdf
    pisa_status = pisa.CreatePDF(
        html, dest=response, link_callback=link_callback)
    
    # return response
    if pisa_status.err:
        return HttpResponse('Nous avons rencontré des erreurs <pre>' + html + '</pre>')
    return response

def export_to_pdf(title, data, filename, template=None, context=None, user=None):
    """
    Exporte des données au format PDF en mode paysage avec logo
    
    Args:
        title (str): Titre du document
        data (list): Liste de dictionnaires contenant les données à exporter
        filename (str): Nom du fichier de sortie
        template (str, optional): Template HTML à utiliser
        context (dict, optional): Contexte pour le template
        user (User, optional): L'utilisateur qui demande l'exportation
    
    Returns:
        HttpResponse: Réponse HTTP avec le fichier PDF
    """
    buffer = io.BytesIO()
    # Utiliser le mode paysage pour avoir plus d'espace horizontal
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=landscape(A4), 
        title=title,
        leftMargin=20,
        rightMargin=20,
        topMargin=30,
        bottomMargin=30
    )
    styles = getSampleStyleSheet()
    elements = []
    
    # Ajouter le logo MAMO
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logo_path = os.path.join(base_dir, 'static', 'img', 'logo_mamo.png')
    
    if os.path.exists(logo_path):
        img_width = 100  # Largeur du logo en pixels
        img_height = 50  # Hauteur approximative, sera ajustée proportionnellement
        logo = os.path.abspath(logo_path)
        elements.append(Image(logo, width=img_width, height=img_height, hAlign='CENTER'))
        elements.append(Spacer(1, 10))  # Espacement après le logo
    
    # Créer un style personnalisé pour le titre
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=1,  # Centré
        spaceAfter=12
    )
    
    # Ajouter le titre
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 10))
    
    # Ajouter la date et le demandeur
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=1,
        spaceAfter=5
    )
    elements.append(Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y %H:%M')}", date_style))
    
    # Ajouter le nom du demandeur si disponible
    if user:
        user_style = ParagraphStyle(
            'UserStyle',
            parent=styles['Normal'],
            fontSize=12,
            alignment=1,
            spaceAfter=15,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        )
        elements.append(Paragraph(f"Demandeur: {user.get_full_name() or user.username}", user_style))
    else:
        elements.append(Spacer(1, 15))  # Espacement supplémentaire si pas de demandeur
    
    # Préparer les en-têtes et les données
    if data and isinstance(data[0], dict):
        headers = list(data[0].keys())
        
        # Définir des poids personnalisés pour les colonnes en fonction de leur contenu
        col_width_mapping = {
            'Véhicule': 0.7,
            'Marque/Modèle': 1.0,
            'Station': 0.8,
            'Date': 0.9,
            'Kilométrage avant': 0.9,
            'Kilométrage après': 0.9,
            'Kilométrage': 0.7,
            'Distance': 0.6,
            'Distance parcourue': 0.8,
            'Litres': 0.5,
            'Prix unitaire': 0.7,
            'Coût total': 0.7,
            'Consommation': 0.9,
            'Consommation (L/100km)': 1.0,
            'Commentaires': 1.5,
            'Garage': 0.9,
            'Motif': 1.2,
            'Statut': 0.7,
            'Coût': 0.6,
        }
        
        # Calculer les largeurs de colonnes
        available_width = landscape(A4)[0] - 40  # Largeur disponible moins les marges
        
        # Attribuer une largeur par défaut aux colonnes non spécifiées
        col_weights = []
        for header in headers:
            col_weights.append(col_width_mapping.get(header, 1.0))
        
        # Normaliser les poids pour qu'ils somment à 1
        total_weight = sum(col_weights)
        col_weights = [w / total_weight for w in col_weights]
        
        # Calculer les largeurs finales des colonnes
        col_widths = [available_width * w for w in col_weights]
        
        # Préparer les données pour la table avec des paragraphes stylisés pour les en-têtes
        header_style = ParagraphStyle(
            'HeaderStyle',
            parent=styles['Normal'],
            fontSize=10,
            alignment=1,  # Centré
            textColor=colors.whitesmoke,
            fontName='Helvetica-Bold'
        )
        
        # Convertir les en-têtes en paragraphes stylisés
        header_paragraphs = [Paragraph(header, header_style) for header in headers]
        
        # Créer les données de la table avec en-têtes stylisés
        table_data = [header_paragraphs]
        
        # Style pour les cellules normales
        cell_style = ParagraphStyle(
            'CellStyle',
            parent=styles['Normal'],
            fontSize=9,
            alignment=0,  # Gauche
            fontName='Helvetica'
        )
        
        # Ajouter les données
        for item in data:
            row = []
            for header in headers:
                # Convertir chaque valeur en paragraphe stylisé
                value = str(item.get(header, ''))
                row.append(Paragraph(value, cell_style))
            table_data.append(row)
        
        # Créer la table avec les largeurs de colonnes calculées
        table = Table(table_data, repeatRows=1, colWidths=col_widths)
        
        # Styliser la table
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),  # Padding réduit pour maximiser l'espace
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),  # Padding réduit pour maximiser l'espace
        ]))
        
        elements.append(table)
    
    # Générer le PDF
    doc.build(elements)
    
    # Préparer la réponse HTTP
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

def export_to_excel(title, data, filename):
    """
    Exporte des données au format Excel
    
    Args:
        title (str): Titre du document
        data (list): Liste de dictionnaires contenant les données à exporter
        filename (str): Nom du fichier de sortie
    
    Returns:
        HttpResponse: Réponse HTTP avec le fichier Excel
    """
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    
    # Styles
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#4F81BD',
        'color': 'white',
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })
    
    cell_format = workbook.add_format({
        'border': 1,
        'valign': 'vcenter'
    })
    
    title_format = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter'
    })
    
    date_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'italic': True
    })
    
    # Ajouter le titre
    worksheet.merge_range('A1:G1', title, title_format)
    
    # Ajouter la date
    worksheet.merge_range('A2:G2', f"Généré le {datetime.now().strftime('%d/%m/%Y %H:%M')}", date_format)
    
    # Ajouter les en-têtes et les données
    if data and isinstance(data[0], dict):
        headers = list(data[0].keys())
        for col, header in enumerate(headers):
            worksheet.write(3, col, header, header_format)
            worksheet.set_column(col, col, 15)  # Ajuster la largeur de la colonne
        
        # Ajouter les données
        for row_idx, item in enumerate(data):
            for col_idx, header in enumerate(headers):
                value = item.get(header, '')
                worksheet.write(row_idx + 4, col_idx, value, cell_format)
    
    workbook.close()
    
    # Préparer la réponse HTTP
    output.seek(0)
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

def export_to_pdf_with_image(title, data, filename, image_path=None, image_caption=None, user=None):
    """
    Exporte des données au format PDF en mode paysage avec logo et une image supplémentaire
    
    Args:
        title (str): Titre du document
        data (list): Liste de dictionnaires contenant les données à exporter
        filename (str): Nom du fichier de sortie
        image_path (str, optional): Chemin vers l'image à inclure
        image_caption (str, optional): Légende de l'image
        user (User, optional): L'utilisateur qui demande l'exportation
    
    Returns:
        HttpResponse: Réponse HTTP avec le fichier PDF
    """
    buffer = io.BytesIO()
    # Utiliser le mode paysage pour avoir plus d'espace horizontal
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=landscape(A4), 
        title=title,
        leftMargin=20,
        rightMargin=20,
        topMargin=30,
        bottomMargin=30
    )
    styles = getSampleStyleSheet()
    elements = []
    
    # Ajouter le logo ASOFES
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logo_path = os.path.join(base_dir, 'static', 'img', 'logo_mamo.png')
    
    if os.path.exists(logo_path):
        img_width = 100  # Largeur du logo en pixels
        img_height = 50  # Hauteur approximative, sera ajustée proportionnellement
        logo = os.path.abspath(logo_path)
        elements.append(Image(logo, width=img_width, height=img_height, hAlign='CENTER'))
        elements.append(Spacer(1, 10))  # Espacement après le logo
    
    # Créer un style personnalisé pour le titre
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=1,  # Centré
        spaceAfter=12
    )
    
    # Ajouter le titre
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 10))
    
    # Ajouter la date et le demandeur
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=1,
        spaceAfter=5
    )
    elements.append(Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y %H:%M')}", date_style))
    
    # Ajouter le nom du demandeur si disponible
    if user:
        user_style = ParagraphStyle(
            'UserStyle',
            parent=styles['Normal'],
            fontSize=12,
            alignment=1,
            spaceAfter=15,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        )
        elements.append(Paragraph(f"Demandeur: {user.get_full_name() or user.username}", user_style))
    else:
        elements.append(Spacer(1, 15))  # Espacement supplémentaire si pas de demandeur
    
    # Préparer les en-têtes et les données
    if data and isinstance(data[0], dict):
        headers = list(data[0].keys())
        
        # Définir des poids personnalisés pour les colonnes en fonction de leur contenu
        col_width_mapping = {
            'Véhicule': 0.7,
            'Marque/Modèle': 1.0,
            'Station': 0.8,
            'Date': 0.9,
            'Kilométrage avant': 0.9,
            'Kilométrage après': 0.9,
            'Kilométrage': 0.7,
            'Distance': 0.6,
            'Distance parcourue': 0.8,
            'Litres': 0.5,
            'Prix unitaire': 0.7,
            'Coût total': 0.7,
            'Consommation': 0.9,
            'Consommation (L/100km)': 1.0,
            'Commentaires': 1.5,
            'Garage': 0.9,
            'Motif': 1.2,
            'Statut': 0.7,
            'Coût': 0.6,
        }
        
        # Calculer les largeurs de colonnes
        available_width = landscape(A4)[0] - 40  # Largeur disponible moins les marges
        
        # Attribuer une largeur par défaut aux colonnes non spécifiées
        col_weights = []
        for header in headers:
            col_weights.append(col_width_mapping.get(header, 1.0))
        
        # Normaliser les poids pour qu'ils somment à 1
        total_weight = sum(col_weights)
        col_weights = [w / total_weight for w in col_weights]
        
        # Calculer les largeurs finales des colonnes
        col_widths = [available_width * w for w in col_weights]
        
        # Préparer les données pour la table avec des paragraphes stylisés pour les en-têtes
        header_style = ParagraphStyle(
            'HeaderStyle',
            parent=styles['Normal'],
            fontSize=10,
            alignment=1,  # Centré
            textColor=colors.whitesmoke,
            fontName='Helvetica-Bold'
        )
        
        # Convertir les en-têtes en paragraphes stylisés
        header_paragraphs = [Paragraph(header, header_style) for header in headers]
        
        # Créer les données de la table avec en-têtes stylisés
        table_data = [header_paragraphs]
        
        # Style pour les cellules normales
        cell_style = ParagraphStyle(
            'CellStyle',
            parent=styles['Normal'],
            fontSize=9,
            alignment=0,  # Gauche
            fontName='Helvetica'
        )
        
        # Ajouter les données
        for item in data:
            row = []
            for header in headers:
                # Convertir chaque valeur en paragraphe stylisé
                value = str(item.get(header, ''))
                row.append(Paragraph(value, cell_style))
            table_data.append(row)
        
        # Créer la table avec les largeurs de colonnes calculées
        table = Table(table_data, repeatRows=1, colWidths=col_widths)
        
        # Styliser la table
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),  # Padding réduit pour maximiser l'espace
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),  # Padding réduit pour maximiser l'espace
        ]))
        
        elements.append(table)
    
    # Ajouter l'image si elle est fournie
    if image_path and os.path.exists(image_path):
        # Ajouter un espace avant l'image
        elements.append(Spacer(1, 20))
        
        # Ajouter un titre pour l'image
        image_title_style = ParagraphStyle(
            'ImageTitle',
            parent=styles['Heading2'],
            fontSize=14,
            alignment=1,  # Centré
            spaceAfter=10
        )
        elements.append(Paragraph("Photo du reçu", image_title_style))
        
        # Ajouter l'image
        # Calculer les dimensions pour que l'image ne soit pas trop grande
        max_width = landscape(A4)[0] - 100  # Largeur maximale
        max_height = 200  # Hauteur maximale
        
        try:
            from PIL import Image as PILImage
            img = PILImage.open(image_path)
            img_width, img_height = img.size
            
            # Calculer le ratio pour redimensionner l'image
            width_ratio = max_width / img_width
            height_ratio = max_height / img_height
            ratio = min(width_ratio, height_ratio)
            
            new_width = img_width * ratio
            new_height = img_height * ratio
            
            # Ajouter l'image redimensionnée
            elements.append(Image(image_path, width=new_width, height=new_height, hAlign='CENTER'))
            
            # Ajouter une légende si elle est fournie
            if image_caption:
                caption_style = ParagraphStyle(
                    'Caption',
                    parent=styles['Normal'],
                    fontSize=9,
                    alignment=1,  # Centré
                    spaceAfter=10,
                    textColor=colors.grey
                )
                elements.append(Paragraph(image_caption, caption_style))
        except Exception as e:
            # En cas d'erreur, ajouter un message d'erreur
            error_style = ParagraphStyle(
                'Error',
                parent=styles['Normal'],
                fontSize=10,
                alignment=1,  # Centré
                textColor=colors.red
            )
            elements.append(Paragraph(f"Impossible d'afficher l'image: {str(e)}", error_style))
    
    # Générer le PDF
    doc.build(elements)
    
    # Préparer la réponse HTTP
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response
