with open('dispatch/templates/dispatch/dashboard.html', 'w', encoding='utf-8') as f:
    f.write('''{% extends 'base.html' %}
{% load static %}

{% block title %}Tableau de bord - Dispatch{% endblock %}

{% block content %}
<div class="row mb-4">
    <div class="col-12">
        <h1>Tableau de bord - Dispatch</h1>
        <p>Version simplifiée pour test</p>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
    console.log('Page chargée');
</script>
{% endblock %}''') 