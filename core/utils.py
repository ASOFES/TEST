import os
import base64
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders


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
    
    # Ajouter le logo au contexte s'il n'est pas déjà présent
    if 'logo_path' not in context_dict:
        context_dict['logo_path'] = logo_path
    
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
