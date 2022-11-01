# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2018 - 2021 Gemeente Amsterdam
from django.db import migrations


def create_initial_data_departments(apps, schema_editor):
    """Creating initial data for all departments."""
    departments = {
        # code, name,                    intern/extern
        'POA': ('Port of Amsterdam',     'E'),
        'THO': ('THOR',                  'I'),
        'WAT': ('Waternet',              'E'),
        'STW': ('Stadswerken',           'I'),
        'AEG': ('Afval en Grondstoffen', 'I'),
        'ASC': ('Actie Service Centrum', 'I'),
        'POL': ('Politie',               'E'),
        'GGD': ('GGD',                   'E'),
        'VOR': ('V&OR',                  'I'),  # Onderscheid V&OR OVL en V&OR VRI ???
        'OVL': ('V&OR OVL',              'I'),  # Onderscheid V&OR OVL en V&OR VRI ???
        'VRI': ('V&OR VRI',              'I'),  # Onderscheid V&OR OVL en V&OR VRI ???
        'CCA': ('CCA',                   'I'),
        'STL': ('Stadsloket',            'I'),
        'OMG': ('Omgevingsdienst',       'I'),  # Intern/extern ???
        'VTH': ('VTH',                   'I'),  # Wat is VTH ? Intern/Extern ?
        'FB':  ('FB',                    'I'),  # ?? what is FB
    }

    Department = apps.get_model('signals', 'Department')
    for department_code, department_values in departments.items():
        name = department_values[0]
        is_intern = department_values[1] == 'I'
        Department.objects.create(code=department_code, name=name, is_intern=is_intern)


def create_initial_data_categories(apps, schema_editor):
    """Creating initial data for all categories."""
    categories = (('Parkeeroverlast', 'Aanhangers/caravans', 'REST'), ('Gevaarlijk (straat)afval', 'accu', 'REST'), ('Vuil op straat', 'Andere uitwerpselen', 'REST'), ('Gevaarlijk (straat)afval', 'asbest', 'REST'), ('Afval', 'bedrijfsafval', 'REST'), ('Straatverlichting', 'beschadigde lichtmast', 'REST'), ('Singels en sloten', 'beschoeiingen', 'REST'), ('Straatmeubilair kapot', 'bewegwijzering', 'REST'), ('Bomen, planten, gras', 'bloembakken', 'REST'), ('Bomen, planten, gras', 'Bomen', 'REST'), ('Weg (fiets/voet)pad brug', 'boomwortels', 'REST'), ('(Weg)werkzaamheden', 'bouwplaatsen - algemeen', 'REST'), ('Afvalcontainer+Prullenbak', 'Bouw/puincontainer', 'REST'), ('Straatverlichting', 'brandt geen verlichting in gehele straat', 'REST'), ('Wrakken', '(Brom-)fietswrak', 'REST'), ('Weg (fiets/voet)pad brug', 'brug', 'REST'), ('Afvalcontainer+Prullenbak', 'cocon/1100 liter rolcontainer vol', 'REST'), ('Afvalcontainer+Prullenbak', 'Containerruimte markthal', 'REST'), ('Maatregelen COVID -19', 'Controle coronatoegangsbewijs ', 'REST'), ('Dieren', 'Dieren overig', 'REST'), ('Dieren', 'Dode duiven', 'REST'), ('Dieren', 'Dode ratten', 'REST'), ('Dieren', 'Dode vogels', 'REST'), ('Dieren', 'dood dier in/aan water (geen rat/duif)', 'REST'), ('Dieren', 'dood dier op/aan weg (geen rat/duif)', 'REST'), ('Singels en sloten', 'drijfvuil in singel', 'REST'), ('Dieren', 'Duivenoverlast', 'REST'), ('Dieren', 'Eikenprocessierups', 'REST'), ('Weg (fiets/voet)pad brug', 'fietspad', 'REST'), ('Meldkamer Stadsbeheer', 'Flying Squads Schone Stad', 'REST'), ('Meldkamer Stadsbeheer', 'Flying Squads T&H', 'REST'), ('Singels en sloten', 'Fonteinen', 'REST'), ('Vuil op straat', 'Ganzen- of eendenpoep', 'REST'), ('Gevaarlijk (straat)afval', 'gastank/brandblusapparatuur', 'REST'), ('Weg (fiets/voet)pad brug', 'gebiedsgericht', 'REST'), ('Weg (fiets/voet)pad brug', 'gladheid (sneeuw-ijzel-vorst)', 'REST'), ('Afvalcontainer+Prullenbak', 'glascontainer kapot', 'REST'), ('Afvalcontainer+Prullenbak', 'glascontainer vol', 'REST'), ('Vuil op straat', 'glas op straat', 'REST'), ('Graffiti', 'graffiti-discriminerend', 'REST'), ('Graffiti', 'graffiti-overig', 'REST'), ('Bomen, planten, gras', 'Gras', 'REST'), ('Afval', 'Grofvuil in plantsoen', 'REST'), ('Afval', 'Grofvuil op straat', 'REST'), ('Afval', 'grond/zand/grind', 'REST'), ('Parkeeroverlast', 'Hinderlijk geparkeerde (brom-)fiets', 'REST'), ('Vuil op straat', 'Hondenpoep op straat', 'REST'), ('Vuil op straat', 'honden-uitlaatzone', 'REST'), ('Wateroverlast / riolering', 'hoofdriool', 'REST'), ('Afvalcontainer+Prullenbak', 'Huiscontainer(gfe+t/gft) niet geleegd', 'REST'), ('Afvalcontainer+Prullenbak', 'Huiscontainer kapot', 'REST'), ('Afvalcontainer+Prullenbak', 'Huiscontainer(papier) niet geleegd', 'REST'), ('Afvalcontainer+Prullenbak', 'Huiscontainer(rest) niet geleegd', 'REST'), ('Afval', 'huisvuil verkeerd aangeboden', 'REST'), ('Afval', 'huisvuilzakken naast container', 'REST'), ('Afval', 'huisvuilzakken niet opgehaald', 'REST'), ('(Weg)werkzaamheden', 'ingraving - huisaansluiting', 'REST'), ('Gevaarlijk (straat)afval', 'injectienaalden/spuiten', 'REST'), ('Weg (fiets/voet)pad brug', 'invalide-oprit', 'REST'), ('Bomen, planten, gras', 'Japanse Duizendknoop', 'REST'), ('Vuil op straat', 'Kerstboom op straat', 'REST'), ('Afval', 'Klein Afval', 'REST'), ('Gevaarlijk (straat)afval', '(klein) chemisch afval', 'REST'), ('Straatmeubilair kapot', 'klok / uurwerk ', 'REST'), ('Afval', 'koelkast/vriezer', 'REST'), ('Straatverlichting', 'lamp(en) uit', 'REST'), ('Dieren', 'Levende ratten', 'REST'), ('Straatverlichting', 'lichtmastluikje staat open / bedrading zichtbaar', 'REST'), ('Overige onderwerpen', 'Marktvoorzieningen', 'REST'), ('Overige onderwerpen', 'Melding op begraafplaats', 'REST'), ('Gevaarlijk (straat)afval', '(olie)lekkage/morsing', 'REST'), ('Gevaarlijk (straat)afval', '(olie)vaten', 'REST'), ('Gevaarlijk (straat)afval', 'onbekende stoffen', 'REST'), ('Vuil op straat', 'Onkruid in groen', 'REST'), ('Vuil op straat', 'Onkruid op verharding', 'REST'), ('Straatmeubilair kapot', 'openbaar oplaadpunt elektrische auto', 'REST'), ('Overige onderwerpen', 'Openbare werken algemeen', 'REST'), ('Overig', 'Overig', 'REST'), ('Vuil op straat', 'Overlast blad of bloesem', 'REST'), ('Overlast', 'Overlast markten', 'REST'), ('Dieren', 'Overlast wespen, bijen, hommels', 'REST'), ('Afvalcontainer+Prullenbak', 'papiercontainer kapot', 'REST'), ('Afvalcontainer+Prullenbak', 'papiercontainer vol', 'REST'), ('Parkeeroverlast', 'Parkeeroverlast', 'REST'), ('Bomen, planten, gras', 'plantsoenen', 'REST'), ('Wildplakken', 'Posters', 'REST'), ('Afvalcontainer+Prullenbak', 'prullenbak kapot', 'REST'), ('Afvalcontainer+Prullenbak', 'prullenbak vol ', 'REST'), ('Wildplakken', 'Reclamebord', 'REST'), ('Afvalcontainer+Prullenbak', 'restafvalcontainer kapot', 'REST'), ('Afvalcontainer+Prullenbak', 'restafvalcontainer vol', 'REST'), ('Weg (fiets/voet)pad brug', 'rijweg', 'REST'), ('Wateroverlast / riolering', 'Rioolaansluiting (verstopping)', 'REST'), ('Weg (fiets/voet)pad brug', 'roltrap/rolband', 'REST'), ('Wildplakken', 'sandwichborden', 'REST'), ('Straatverlichting', 'scheefstaande lichtmast', 'REST'), ('Overige onderwerpen', 'Schone Stad algemeen', 'REST'), ('Singels en sloten', 'singel ', 'REST'), ('Wateroverlast / riolering', 'slechte/geen afwatering', 'REST'), ('Afval', 'sloopafval', 'REST'), ('Weg (fiets/voet)pad brug', 'sluis', 'REST'), ('Speelplaatsen', 'speelplaats', 'REST'), ('Overige onderwerpen', 'Stadsontwikkeling Algemeen', 'REST'), ('Wateroverlast / riolering', 'stankoverlast', 'REST'), ('Wildplakken', 'Stickers', 'REST'), ('Wateroverlast / riolering', 'storing gemaal', 'REST'), ('Wateroverlast / riolering', 'straatkolk (verstopt)', 'REST'), ('Straatmeubilair kapot', 'straatmeubilair algemeen', 'REST'), ('Straatmeubilair kapot', 'straatnaambord/verkeersbord', 'REST'), ('Parkeeroverlast', 'Te lang geparkeerde (brom-)fiets', 'REST'), ('Afvalcontainer+Prullenbak', 'textielcontainer kapot', 'REST'), ('Afvalcontainer+Prullenbak', 'textielcontainer vol', 'REST'), ('(Weg)werkzaamheden', 'tijdelijke verkeerssituatie', 'REST'), ('Overige onderwerpen', 'Toezicht & Handhaving algemeen', 'REST'), ('Weg (fiets/voet)pad brug', 'tunnels/viaducten', 'REST'), ('Gevaarlijk (straat)afval', 'uitgebrande voertuigen (herstel wegdek)', 'REST'), ('Weg (fiets/voet)pad brug', 'verkeersdrempel', 'REST'), ('Straatverlichting', 'verlichting brandt ook overdag', 'REST'), ('Straatverlichting', 'verlichting overig: (geef omschrijving)', 'REST'), ('Weg (fiets/voet)pad brug', 'voetpad', 'REST'), ('Wateroverlast / riolering', 'Water in de kruipruimte, de kelder of in de tuin', 'REST'), ('Wateroverlast / riolering', 'Water- of rioolpersleiding', 'REST'), ('Straatmeubilair kapot', 'Watertappunt', 'REST'), ('Afvalcontainer+Prullenbak', 'Wijkcontainer (gfe) kapot', 'REST'), ('Afvalcontainer+Prullenbak', 'Wijkcontainer (gfe) vol', 'REST'), ('Winkelwagens', 'winkelwagens', 'REST'), ('Wrakken', 'wrak - auto', 'REST'), ('Singels en sloten', 'zinkvuil/vloeistoffen in singel', 'REST'), ('Vuil op straat', 'zwerfvuil in het water', 'REST'), ('Vuil op straat', 'zwerfvuil in plantsoen', 'REST'), ('Vuil op straat', 'zwerfvuil op straat', 'REST'))

    MainCategory = apps.get_model('signals', 'MainCategory')
    SubCategory = apps.get_model('signals', 'SubCategory')
    i = 0
    for category in categories:
        i += 1
        main_category_name = category[0]
        sub_category_name = category[1]
        handling = category[2]

        # Creating (or get if already exist) `MainCategory` object.
        main_category, _ = MainCategory.objects.get_or_create(name=main_category_name)
        # Creating `SubCategory` object.
        sub_category = SubCategory.objects.create(
            code=f'F{i:02d}',
            main_category=main_category,
            name=sub_category_name,
            handling=handling
        )


class Migration(migrations.Migration):

    dependencies = [
        ('signals', '0008_department_maincategory_subcategory'),
    ]

    operations = [
        migrations.RunPython(create_initial_data_departments),
        migrations.RunPython(create_initial_data_categories),
    ]
