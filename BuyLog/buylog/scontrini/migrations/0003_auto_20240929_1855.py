from django.db import migrations, models


def populate_totale(apps, schema_editor):
    Scontrino = apps.get_model('scontrini', 'Scontrino')
    for scontrino in Scontrino.objects.all():
        # Calcola il totale per ogni scontrino
        totale = sum(item.prezzo_unitario *
                     item.quantita for item in scontrino.prodotti.all())
        scontrino.totale = totale
        scontrino.save()


class Migration(migrations.Migration):

    dependencies = [
        ('scontrini', '0002_alter_listaprodotti_options_alter_negozio_options_and_more'),
    ]

    operations = [
        migrations.RunPython(populate_totale),
    ]
