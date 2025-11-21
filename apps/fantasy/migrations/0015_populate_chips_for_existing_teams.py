from django.db import migrations


def create_chips_for_existing_teams(apps, schema_editor):
    """Create chips for all existing fantasy teams"""
    FantasyTeam = apps.get_model('fantasy', 'FantasyTeam')
    Chip = apps.get_model('fantasy', 'Chip')
    
    chip_types = ['TC', 'BB', 'WC']
    
    for team in FantasyTeam.objects.all():
        for chip_type in chip_types:
            Chip.objects.get_or_create(
                fantasy_team=team,
                chip_type=chip_type,
                defaults={'is_used': False}
            )


def reverse_chips(apps, schema_editor):
    """Remove all chips"""
    Chip = apps.get_model('fantasy', 'Chip')
    Chip.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('fantasy', '0014_chip_teamselection_active_chip_and_more'),
    ]

    operations = [
        migrations.RunPython(create_chips_for_existing_teams, reverse_chips),
    ]
