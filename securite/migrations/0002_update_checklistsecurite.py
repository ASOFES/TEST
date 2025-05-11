# Generated manually

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('securite', '0001_initial'),
    ]

    operations = [
        # Renommer le champ agent_securite en controleur
        migrations.RenameField(
            model_name='checklistsecurite',
            old_name='agent_securite',
            new_name='controleur',
        ),
        # Renommer le champ date_check en date_creation
        migrations.RenameField(
            model_name='checklistsecurite',
            old_name='date_check',
            new_name='date_creation',
        ),
        # Renommer le champ commentaires en observations
        migrations.RenameField(
            model_name='checklistsecurite',
            old_name='commentaires',
            new_name='observations',
        ),
        # Supprimer les champs obsolètes
        migrations.RemoveField(
            model_name='checklistsecurite',
            name='type_check',
        ),
        migrations.RemoveField(
            model_name='checklistsecurite',
            name='parebrise_avant',
        ),
        migrations.RemoveField(
            model_name='checklistsecurite',
            name='parebrise_arriere',
        ),
        migrations.RemoveField(
            model_name='checklistsecurite',
            name='retroviseur_gauche',
        ),
        migrations.RemoveField(
            model_name='checklistsecurite',
            name='retroviseur_droit',
        ),
        migrations.RemoveField(
            model_name='checklistsecurite',
            name='clignotant',
        ),
        migrations.RemoveField(
            model_name='checklistsecurite',
            name='feu_arriere_gauche',
        ),
        migrations.RemoveField(
            model_name='checklistsecurite',
            name='feu_arriere_droit',
        ),
        migrations.RemoveField(
            model_name='checklistsecurite',
            name='feu_position_gauche',
        ),
        migrations.RemoveField(
            model_name='checklistsecurite',
            name='feu_position_droit',
        ),
        # Ajouter les nouveaux champs
        migrations.AddField(
            model_name='checklistsecurite',
            name='date_controle',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='checklistsecurite',
            name='lieu_controle',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='checklistsecurite',
            name='statut',
            field=models.CharField(choices=[('conforme', 'Conforme'), ('anomalie_mineure', 'Anomalie mineure'), ('non_conforme', 'Non conforme')], default='conforme', max_length=20),
        ),
        migrations.AddField(
            model_name='checklistsecurite',
            name='phares_avant',
            field=models.CharField(choices=[('ok', 'OK'), ('defectueux', 'Défectueux')], default='ok', max_length=20),
        ),
        migrations.AddField(
            model_name='checklistsecurite',
            name='phares_arriere',
            field=models.CharField(choices=[('ok', 'OK'), ('defectueux', 'Défectueux')], default='ok', max_length=20),
        ),
        migrations.AddField(
            model_name='checklistsecurite',
            name='clignotants',
            field=models.CharField(choices=[('ok', 'OK'), ('defectueux', 'Défectueux')], default='ok', max_length=20),
        ),
        migrations.AddField(
            model_name='checklistsecurite',
            name='etat_pneus',
            field=models.CharField(choices=[('ok', 'OK'), ('usure', 'Usure'), ('critique', 'Critique')], default='ok', max_length=20),
        ),
        migrations.AddField(
            model_name='checklistsecurite',
            name='carrosserie',
            field=models.CharField(choices=[('ok', 'OK'), ('rayures', 'Rayures mineures'), ('dommages', 'Dommages importants')], default='ok', max_length=20),
        ),
        migrations.AddField(
            model_name='checklistsecurite',
            name='tableau_bord',
            field=models.CharField(choices=[('ok', 'OK'), ('voyants', 'Voyants allumés')], default='ok', max_length=20),
        ),
        migrations.AddField(
            model_name='checklistsecurite',
            name='freins',
            field=models.CharField(choices=[('ok', 'OK'), ('usure', 'Usure'), ('defectueux', 'Défectueux')], default='ok', max_length=20),
        ),
        migrations.AddField(
            model_name='checklistsecurite',
            name='ceintures',
            field=models.CharField(choices=[('ok', 'OK'), ('defectueuses', 'Défectueuses')], default='ok', max_length=20),
        ),
        migrations.AddField(
            model_name='checklistsecurite',
            name='proprete',
            field=models.CharField(choices=[('ok', 'OK'), ('sale', 'Sale')], default='ok', max_length=20),
        ),
        migrations.AddField(
            model_name='checklistsecurite',
            name='carte_grise',
            field=models.CharField(choices=[('present', 'Présente'), ('absent', 'Absente')], default='present', max_length=20),
        ),
        migrations.AddField(
            model_name='checklistsecurite',
            name='assurance',
            field=models.CharField(choices=[('present', 'Présente'), ('absent', 'Absente')], default='present', max_length=20),
        ),
        migrations.AddField(
            model_name='checklistsecurite',
            name='triangle',
            field=models.CharField(choices=[('present', 'Présent'), ('absent', 'Absent')], default='present', max_length=20),
        ),
        migrations.AddField(
            model_name='checklistsecurite',
            name='gilet',
            field=models.CharField(choices=[('present', 'Présent'), ('absent', 'Absent')], default='present', max_length=20),
        ),
        # Ajouter les options Meta
        migrations.AlterModelOptions(
            name='checklistsecurite',
            options={'ordering': ['-date_controle'], 'verbose_name': 'Checklist de sécurité', 'verbose_name_plural': 'Checklists de sécurité'},
        ),
    ]
