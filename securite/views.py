from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.template.loader import get_template
from django.utils import timezone
from django.conf import settings
from datetime import datetime
import io

from core.models import Vehicule, ActionTraceur
from core.decorators import securite_required
from .models import CheckListSecurite
from .forms import ChecklistSecuriteForm

# Tentative d'importation de xhtml2pdf pour la génération de PDF
try:
    from xhtml2pdf import pisa
    PDF_ENABLED = True
except ImportError:
    PDF_ENABLED = False

@login_required
@securite_required
def dashboard(request):
    """Tableau de bord pour le personnel de sécurité"""
    # Récupérer tous les véhicules pour le filtre
    vehicules = Vehicule.objects.all().order_by('immatriculation')
    
    # Filtres
    statut_filter = request.GET.get('statut')
    vehicule_filter = request.GET.get('vehicule')
    date_debut_filter = request.GET.get('date_debut')
    lieu_controle_filter = request.GET.get('lieu_controle')
    
    # Construire la requête de base
    checklists_query = CheckListSecurite.objects.all().order_by('-date_controle')
    
    # Appliquer les filtres
    if statut_filter:
        checklists_query = checklists_query.filter(statut=statut_filter)
    
    if vehicule_filter:
        checklists_query = checklists_query.filter(vehicule_id=vehicule_filter)
    
    if lieu_controle_filter:
        checklists_query = checklists_query.filter(lieu_controle__icontains=lieu_controle_filter)
    
    if date_debut_filter:
        try:
            date_debut = datetime.strptime(date_debut_filter, '%Y-%m-%d')
            checklists_query = checklists_query.filter(date_controle__date__gte=date_debut)
        except ValueError:
            pass
    
    # Paginer les résultats
    paginator = Paginator(checklists_query, 10)  # 10 checklists par page
    page_number = request.GET.get('page')
    checklists = paginator.get_page(page_number)
    
    # Statistiques
    stats = {
        'total': CheckListSecurite.objects.count(),
        'conformes': CheckListSecurite.objects.filter(statut='conforme').count(),
        'anomalies_mineures': CheckListSecurite.objects.filter(statut='anomalie_mineure').count(),
        'non_conformes': CheckListSecurite.objects.filter(statut='non_conforme').count(),
    }
    
    context = {
        'checklists': checklists,
        'vehicules': vehicules,
        'stats': stats,
    }
    
    return render(request, 'securite/dashboard_simple.html', context)

@login_required
@securite_required
def nouvelle_checklist(request):
    """Créer une nouvelle checklist de sécurité"""
    if request.method == 'POST':
        form = ChecklistSecuriteForm(request.POST)
        if form.is_valid():
            # Enregistrer la checklist avec l'utilisateur actuel comme agent de sécurité
            checklist = form.save(commit=True, controleur=request.user)
            
            # Message de succès en fonction du statut
            if checklist.statut == 'conforme':
                messages.success(request, f'Check-list créée avec succès. Le véhicule {checklist.vehicule.immatriculation} est conforme.')
            elif checklist.statut == 'anomalie_mineure':
                messages.warning(request, f'Check-list créée avec succès. Le véhicule {checklist.vehicule.immatriculation} présente des anomalies mineures.')
            else:  # non_conforme
                messages.error(request, f'Check-list créée avec succès. Le véhicule {checklist.vehicule.immatriculation} n\'est pas conforme et ne peut pas être utilisé.')
            
            return redirect('securite:detail_checklist', checklist.id)
    else:
        form = ChecklistSecuriteForm()
    
    context = {
        'form': form,
        'vehicules': Vehicule.objects.all().order_by('immatriculation'),
    }
    
    return render(request, 'securite/nouvelle_checklist_simple.html', context)

@login_required
@securite_required
def detail_checklist(request, checklist_id):
    """Afficher les détails d'une checklist de sécurité"""
    checklist = get_object_or_404(CheckListSecurite, id=checklist_id)
    
    # Récupérer l'historique des actions liées à ce véhicule
    historique = ActionTraceur.objects.filter(
        Q(action__icontains=f"check-list") & Q(action__icontains=checklist.vehicule.immatriculation)
    ).order_by('-date_action')[:10]  # Limiter aux 10 dernières actions
    
    context = {
        'checklist': checklist,
        'historique': historique,
    }
    
    return render(request, 'securite/detail_checklist_simple.html', context)

def link_callback(uri, rel):
    """Convertit les URI en chemins absolus pour xhtml2pdf"""
    import os
    
    # Utiliser le chemin absolu du projet
    sUrl = settings.STATIC_URL        # Typiquement /static/
    sRoot = settings.STATIC_ROOT      # Typiquement /home/userx/project/static/
    mUrl = settings.MEDIA_URL         # Typiquement /media/
    mRoot = settings.MEDIA_ROOT       # Typiquement /home/userx/project/media/

    # Convertir l'URI en chemin de fichier
    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    elif uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))
    else:
        return uri  # Gérer les URI externes

    # Vérifier si le fichier existe
    if not os.path.isfile(path):
        raise Exception(f'Le fichier {path} n\'existe pas')
        
    return path

def pdf_checklist(request, checklist_id):
    """Générer un PDF de la checklist de sécurité"""
    if not PDF_ENABLED:
        messages.error(request, "La génération de PDF n'est pas disponible. Veuillez installer xhtml2pdf.")
        return redirect('securite:detail_checklist', checklist_id)
    
    checklist = get_object_or_404(CheckListSecurite, id=checklist_id)
    
    # Préparer le contexte pour le template
    context = {
        'checklist': checklist,
        'date_generation': timezone.now(),
        'MEDIA_URL': settings.MEDIA_URL,  # Ajouter l'URL des médias au contexte
    }
    
    # Charger le template
    template = get_template('securite/pdf_checklist.html')
    html = template.render(context)
    
    # Créer une réponse HTTP avec le PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="checklist_{checklist_id}.pdf"'
    
    # Générer le PDF avec le gestionnaire de liens personnalisé
    pdf_status = pisa.CreatePDF(
        io.BytesIO(html.encode("UTF-8")),
        dest=response,
        link_callback=link_callback
    )
    
    if pdf_status.err:
        messages.error(request, "Une erreur est survenue lors de la génération du PDF.")
        return redirect('securite:detail_checklist', checklist_id)
    
    return response
