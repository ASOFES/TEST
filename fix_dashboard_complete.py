with open('dispatch/templates/dispatch/dashboard.html', 'w', encoding='utf-8') as f:
    f.write('''{% extends 'base.html' %}
{% load static %}

{% block title %}Tableau de bord - Dispatch{% endblock %}

{% block content %}
<div class="row mb-4">
    <div class="col-12">
        <h1><i class="fas fa-tachometer-alt me-2"></i>Tableau de bord - Dispatch</h1>
        <p class="lead">Gérez les demandes de mission et assignez les chauffeurs et véhicules.</p>
    </div>
</div>

<div class="row mb-4">
    <div class="col-md-3">
        <div class="card mb-4">
            <div class="card-header module-dispatch text-white">
                <h5 class="mb-0"><i class="fas fa-filter me-2"></i>Filtres</h5>
            </div>
            <div class="card-body">
                <form method="get" action="{% url 'dispatch:dashboard' %}">
                    <div class="mb-3">
                        <label for="statut" class="form-label">Statut</label>
                        <select name="statut" id="statut" class="form-select">
                            <option value="">Tous les statuts</option>
                            <option value="en_attente" {% if request.GET.statut == 'en_attente' %}selected{% endif %}>En attente</option>
                            <option value="validee" {% if request.GET.statut == 'validee' %}selected{% endif %}>Validée</option>
                            <option value="refusee" {% if request.GET.statut == 'refusee' %}selected{% endif %}>Refusée</option>
                            <option value="en_cours" {% if request.GET.statut == 'en_cours' %}selected{% endif %}>En cours</option>
                            <option value="terminee" {% if request.GET.statut == 'terminee' %}selected{% endif %}>Terminée</option>
                        </select>
                    </div>
                    
                    <div class="mb-3">
                        <label for="date_debut" class="form-label">Date début</label>
                        <input type="date" name="date_debut" id="date_debut" class="form-control" value="{{ request.GET.date_debut|default:'' }}">
                    </div>
                    
                    <div class="mb-3">
                        <label for="date_fin" class="form-label">Date fin</label>
                        <input type="date" name="date_fin" id="date_fin" class="form-control" value="{{ request.GET.date_fin|default:'' }}">
                    </div>
                    
                    <div class="mb-3">
                        <label for="recherche" class="form-label">Recherche</label>
                        <input type="text" name="recherche" id="recherche" class="form-control" placeholder="Nom, destination..." value="{{ request.GET.recherche|default:'' }}">
                    </div>
                    
                    <div class="mb-3">
                        <label for="tri" class="form-label">Trier par</label>
                        <select name="tri" id="tri" class="form-select">
                            <option value="date_demande" {% if request.GET.tri == 'date_demande' or not request.GET.tri %}selected{% endif %}>Date de demande</option>
                            <option value="date_souhaitee" {% if request.GET.tri == 'date_souhaitee' %}selected{% endif %}>Date souhaitée</option>
                            <option value="demandeur" {% if request.GET.tri == 'demandeur' %}selected{% endif %}>Demandeur</option>
                            <option value="destination" {% if request.GET.tri == 'destination' %}selected{% endif %}>Destination</option>
                        </select>
                    </div>
                    
                    <div class="d-grid gap-2">
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-search me-2"></i>Filtrer
                        </button>
                        <a href="{% url 'dispatch:dashboard' %}" class="btn btn-secondary">
                            <i class="fas fa-undo me-2"></i>Réinitialiser
                        </a>
                    </div>
                </form>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header module-dispatch text-white">
                <h5 class="mb-0"><i class="fas fa-chart-pie me-2"></i>Statistiques</h5>
            </div>
            <div class="card-body">
                <div class="mb-3">
                    <h6>Demandes par statut</h6>
                    <div class="progress" style="height: 25px;">
                        {% if stats.total > 0 %}
                        <div class="progress-bar bg-warning" role="progressbar" style="width: {{ stats.en_attente_percent }}%;" title="En attente: {{ stats.en_attente }}">{{ stats.en_attente }}</div>
                        <div class="progress-bar bg-success" role="progressbar" style="width: {{ stats.validee_percent }}%;" title="Validée: {{ stats.validee }}">{{ stats.validee }}</div>
                        <div class="progress-bar bg-danger" role="progressbar" style="width: {{ stats.refusee_percent }}%;" title="Refusée: {{ stats.refusee }}">{{ stats.refusee }}</div>
                        <div class="progress-bar bg-primary" role="progressbar" style="width: {{ stats.en_cours_percent }}%;" title="En cours: {{ stats.en_cours }}">{{ stats.en_cours }}</div>
                        <div class="progress-bar bg-secondary" role="progressbar" style="width: {{ stats.terminee_percent }}%;" title="Terminée: {{ stats.terminee }}">{{ stats.terminee }}</div>
                        {% else %}
                        <div class="progress-bar" role="progressbar" style="width: 100%;">Aucune donnée</div>
                        {% endif %}
                    </div>
                    <small class="text-muted">Total: {{ stats.total }} demandes</small>
                </div>
            </div>
        </div>
    </div>
    
    <div class="col-md-9">
        <div class="card">
            <div class="card-header module-dispatch text-white d-flex justify-content-between align-items-center">
                <h5 class="mb-0"><i class="fas fa-list me-2"></i>Liste des demandes</h5>
                <div class="dropdown">
                    <button class="btn btn-sm btn-light dropdown-toggle" type="button" id="exportDropdown" data-bs-toggle="dropdown" aria-expanded="false">
                        <i class="fas fa-download me-2"></i>Exporter
                    </button>
                    <ul class="dropdown-menu" aria-labelledby="exportDropdown">
                        <li><a class="dropdown-item" href="{% url 'dispatch:courses_list_pdf' %}{% if request.GET.statut %}?statut={{ request.GET.statut }}{% endif %}{% if request.GET.date_debut %}&date_debut={{ request.GET.date_debut }}{% endif %}{% if request.GET.date_fin %}&date_fin={{ request.GET.date_fin }}{% endif %}">
                            <i class="fas fa-file-pdf me-2 text-danger"></i>Exporter en PDF
                        </a></li>
                        <li><a class="dropdown-item" href="{% url 'dispatch:courses_list_excel' %}{% if request.GET.statut %}?statut={{ request.GET.statut }}{% endif %}{% if request.GET.date_debut %}&date_debut={{ request.GET.date_debut }}{% endif %}{% if request.GET.date_fin %}&date_fin={{ request.GET.date_fin }}{% endif %}">
                            <i class="fas fa-file-excel me-2 text-success"></i>Exporter en Excel
                        </a></li>
                    </ul>
                </div>
            </div>
            <div class="card-body">
                {% if demandes %}
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Date demande</th>
                                <th>Demandeur</th>
                                <th>Point d'embarquement</th>
                                <th>Destination</th>
                                <th>Date souhaitée</th>
                                <th>Statut</th>
                                <th>Chauffeur</th>
                                <th>Véhicule</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for demande in demandes %}
                            <tr>
                                <td>{{ demande.id }}</td>
                                <td>{{ demande.date_demande|date:"d/m/Y H:i" }}</td>
                                <td>
                                    {% if demande.demandeur %}
                                        {% if demande.demandeur.get_full_name %}
                                            {{ demande.demandeur.get_full_name }}
                                        {% else %}
                                            {{ demande.demandeur.username }}
                                        {% endif %}
                                        {% if demande.demandeur.email %}
                                            <br><small class="text-muted">{{ demande.demandeur.email }}</small>
                                        {% endif %}
                                    {% else %}
                                        N/A
                                    {% endif %}
                                </td>
                                <td>{{ demande.point_embarquement }}</td>
                                <td>{{ demande.destination }}</td>
                                <td>{{ demande.date_souhaitee|date:"d/m/Y H:i" }}</td>
                                <td>
                                    {% if demande.statut == 'en_attente' %}
                                    <span class="badge bg-warning">En attente</span>
                                    {% elif demande.statut == 'validee' %}
                                    <span class="badge bg-success">Validée</span>
                                    {% elif demande.statut == 'refusee' %}
                                    <span class="badge bg-danger">Refusée</span>
                                    {% elif demande.statut == 'en_cours' %}
                                    <span class="badge bg-primary">En cours</span>
                                    {% elif demande.statut == 'terminee' %}
                                    <span class="badge bg-secondary">Terminée</span>
                                    {% else %}
                                    <span class="badge bg-dark">{{ demande.get_statut_display }}</span>
                                    {% endif %}
                                </td>
                                <td>{{ demande.chauffeur.get_full_name|default:"Non assigné" }}</td>
                                <td>{{ demande.vehicule.immatriculation|default:"Non assigné" }}</td>
                                <td>
                                    <a href="{% url 'dispatch:detail_demande' demande.id %}" class="btn btn-sm btn-info">
                                        <i class="fas fa-eye"></i>
                                    </a>
                                    {% if demande.statut == 'en_attente' %}
                                    <a href="{% url 'dispatch:traiter_demande' demande.id %}" class="btn btn-sm btn-primary">
                                        <i class="fas fa-tasks"></i>
                                    </a>
                                    {% endif %}
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                
                <!-- Pagination -->
                {% if demandes.paginator.num_pages > 0 %}
                <div class="d-flex justify-content-center mt-4">
                    <nav aria-label="Pagination des demandes">
                        <ul class="pagination">
                            {% if demandes.has_previous %}
                                <li class="page-item">
                                    <a class="page-link" href="?page=1{% if request.GET.statut %}&statut={{ request.GET.statut }}{% endif %}{% if request.GET.date_debut %}&date_debut={{ request.GET.date_debut }}{% endif %}{% if request.GET.date_fin %}&date_fin={{ request.GET.date_fin }}{% endif %}{% if request.GET.recherche %}&recherche={{ request.GET.recherche }}{% endif %}{% if request.GET.tri %}&tri={{ request.GET.tri }}{% endif %}" aria-label="Première">
                                        <span aria-hidden="true">&laquo;&laquo;</span>
                                    </a>
                                </li>
                                <li class="page-item">
                                    <a class="page-link" href="?page={{ demandes.previous_page_number }}{% if request.GET.statut %}&statut={{ request.GET.statut }}{% endif %}{% if request.GET.date_debut %}&date_debut={{ request.GET.date_debut }}{% endif %}{% if request.GET.date_fin %}&date_fin={{ request.GET.date_fin }}{% endif %}{% if request.GET.recherche %}&recherche={{ request.GET.recherche }}{% endif %}{% if request.GET.tri %}&tri={{ request.GET.tri }}{% endif %}" aria-label="Précédente">
                                        <span aria-hidden="true">&laquo;</span>
                                    </a>
                                </li>
                            {% else %}
                                <li class="page-item disabled">
                                    <a class="page-link" href="#" aria-label="Première">
                                        <span aria-hidden="true">&laquo;&laquo;</span>
                                    </a>
                                </li>
                                <li class="page-item disabled">
                                    <a class="page-link" href="#" aria-label="Précédente">
                                        <span aria-hidden="true">&laquo;</span>
                                    </a>
                                </li>
                            {% endif %}
                            
                            {% for i in demandes.paginator.page_range %}
                                {% if demandes.number == i %}
                                    <li class="page-item active" aria-current="page">
                                        <span class="page-link">{{ i }}</span>
                                    </li>
                                {% elif i > demandes.number|add:'-3' and i < demandes.number|add:'3' %}
                                    <li class="page-item">
                                        <a class="page-link" href="?page={{ i }}{% if request.GET.statut %}&statut={{ request.GET.statut }}{% endif %}{% if request.GET.date_debut %}&date_debut={{ request.GET.date_debut }}{% endif %}{% if request.GET.date_fin %}&date_fin={{ request.GET.date_fin }}{% endif %}{% if request.GET.recherche %}&recherche={{ request.GET.recherche }}{% endif %}{% if request.GET.tri %}&tri={{ request.GET.tri }}{% endif %}">{{ i }}</a>
                                    </li>
                                {% endif %}
                            {% endfor %}
                            
                            {% if demandes.has_next %}
                                <li class="page-item">
                                    <a class="page-link" href="?page={{ demandes.next_page_number }}{% if request.GET.statut %}&statut={{ request.GET.statut }}{% endif %}{% if request.GET.date_debut %}&date_debut={{ request.GET.date_debut }}{% endif %}{% if request.GET.date_fin %}&date_fin={{ request.GET.date_fin }}{% endif %}{% if request.GET.recherche %}&recherche={{ request.GET.recherche }}{% endif %}{% if request.GET.tri %}&tri={{ request.GET.tri }}{% endif %}" aria-label="Suivante">
                                        <span aria-hidden="true">&raquo;</span>
                                    </a>
                                </li>
                                <li class="page-item">
                                    <a class="page-link" href="?page={{ demandes.paginator.num_pages }}{% if request.GET.statut %}&statut={{ request.GET.statut }}{% endif %}{% if request.GET.date_debut %}&date_debut={{ request.GET.date_debut }}{% endif %}{% if request.GET.date_fin %}&date_fin={{ request.GET.date_fin }}{% endif %}{% if request.GET.recherche %}&recherche={{ request.GET.recherche }}{% endif %}{% if request.GET.tri %}&tri={{ request.GET.tri }}{% endif %}" aria-label="Dernière">
                                        <span aria-hidden="true">&raquo;&raquo;</span>
                                    </a>
                                </li>
                            {% else %}
                                <li class="page-item disabled">
                                    <a class="page-link" href="#" aria-label="Suivante">
                                        <span aria-hidden="true">&raquo;</span>
                                    </a>
                                </li>
                                <li class="page-item disabled">
                                    <a class="page-link" href="#" aria-label="Dernière">
                                        <span aria-hidden="true">&raquo;&raquo;</span>
                                    </a>
                                </li>
                            {% endif %}
                        </ul>
                    </nav>
                </div>
                
                <div class="text-center mt-2">
                    <small class="text-muted">
                        Page {{ demandes.number }} sur {{ demandes.paginator.num_pages }} 
                        ({{ demandes.paginator.count }} demandes au total)
                    </small>
                </div>
                {% endif %}
                {% else %}
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i>Aucune demande trouvée.
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
    document.addEventListener('DOMContentLoaded', function() {
        // Initialiser les sélecteurs avec Select2 pour une meilleure expérience utilisateur
        if (typeof $.fn.select2 !== 'undefined') {
            $('#statut, #tri').select2({
                theme: 'bootstrap-5',
                width: '100%'
            });
        }
        
        // Mettre en évidence les résultats de recherche
        const searchTerm = '{{ request.GET.recherche }}';
        if (searchTerm) {
            // Fonction pour mettre en évidence le texte
            function highlightText(element) {
                const text = element.textContent;
                if (text && text.toLowerCase().includes(searchTerm.toLowerCase())) {
                    const regex = new RegExp(searchTerm, 'gi');
                    element.innerHTML = text.replace(regex, match => `<mark class="bg-warning">${match}</mark>`);
                }
            }
            
            // Appliquer la mise en évidence aux cellules du tableau
            const tableCells = document.querySelectorAll('table tbody td');
            tableCells.forEach(cell => {
                if (!cell.querySelector('a, button, .badge')) { // Ne pas modifier les cellules avec des éléments interactifs
                    highlightText(cell);
                }
            });
        }
    });
</script>
{% endblock %}''') 