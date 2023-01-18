import json
import os
import django
import requests
import mimetypes
import re
import pytz

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "umisconfig.settings")
django.setup()
from units.models import *
from umisconfig.settings import *
from bs4 import BeautifulSoup
from datetime import datetime
from dashboard.repsys_ingest import *
from datetime import date


choice = 'runwd'

# checked 1/12/23
if choice == 'runiec':
    # read the units data file and add the units to the entities table
    rsid = 15
    units = getrepsystemdata(rsid)
    for unit in units:
        ent, created = Entities.objects.get_or_create(
            repsys='iec',
            repsystem_id=rsid,
            name=unit['name'],
            symbol=unit['shortname'],
            quantity=unit['quantity'],
            lang='en',
            value=unit['code'],
            source='iec',
            comment=unit['definition']
        )
        ent.save()
        if created:
            print("added '" + str(ent.value) + "' (" + str(ent.id) + ")")
        else:
            print("found '" + str(ent.value) + "' (" + str(ent.id) + ")")

        # add unece equivalent if available
        if unit['unece'] != "":
            ent, created = Entities.objects.get_or_create(
                repsys='unece',
                repsystem_id=16,
                name=unit['name'],
                quantity=unit['quantity'],
                lang='en',
                value=unit['unece'],
                source='iec'
            )
            ent.save()
            if created:
                print("added '" + str(ent.value) + "' (" + str(ent.id) + ")")
            else:
                print("found '" + str(ent.value) + "' (" + str(ent.id) + ")")

# checked 1/10/23
if choice == 'runwd':
    # load current file
    rsid = 7
    data = getrepsystemdata(rsid)
    for hit in data['results']['bindings']:
        # check the hits for any that are not useful
        if "http://www.wikidata.org/entity/Q" not in hit['unit']['value']:
            continue

        quant = None
        find1 = hit['subclass1Label']['value'].find("unit of ")
        find2 = hit['subclass2Label']['value'].find("unit of ")
        if find1 == 0:
            quant = hit['subclass1Label']['value'].replace("unit of ", "")
        elif find1 > 0:
            quant = hit['subclass1Label']['value']

        if not quant:
            if find2 == 0:
                quant = hit['subclass2Label']['value'].replace("unit of ", "")
            elif find2 > 0:
                quant = hit['subclass2Label']['value']

        sivals = ["SI unit", "SI base unit", "SI or accepted non-SI unit", "SI-accepted non-SI unit",
                  "SI derived unit", "SI unit with special name", "coherent SI unit"]
        if not quant:
            if hit['subclass1Label']['value'] in sivals:
                quant = "SI unit"
            if hit['subclass2Label']['value'] in sivals:
                quant = "SI unit"

        wdid = hit['unit']['value'].replace("http://www.wikidata.org/entity/", "")
        if ('qudt' or 'ncit' or 'ucum' or 'unece' or 'uom2' or 'wolf' or 'iev' or 'wur' or 'igb') in hit:
            repsyss = []
            if 'qudt' in hit:
                repsyss.append({'name': "qudt", 'rsid': 10})
            if 'ncit' in hit:
                repsyss.append({'name': "ncit", 'rsid': 9})
            if 'ucum' in hit:
                repsyss.append({'name': "ucum", 'rsid': 2})
            if 'unece' in hit:
                repsyss.append({'name': "unece", 'rsid': 6})
            if 'uom2' in hit:
                repsyss.append({'name': "uom2", 'rsid': 13})
            if 'wolf' in hit:
                repsyss.append({'name': "wolf", 'rsid': 20})
            if 'iev' in hit:
                repsyss.append({'name': "iev", 'rsid': 21})
            if 'wur' in hit:
                repsyss.append({'name': "wur", 'rsid': 23})
            if 'igb' in hit:
                repsyss.append({'name': "igb", 'rsid': 3})

            for repsys in repsyss:
                ent, created = Entities.objects.get_or_create(
                    name=hit['unitLabel']['value'],
                    repsys=repsys['name'],
                    repsystem_id=repsys['rsid'],
                    quantity=quant,
                    value=hit[repsys['name']]['value'],
                    source='wikidata')
                ent.lastupdate = date.today()
                ent.save()
                if created:
                    print("added '" + ent.value + "' (" + str(ent.id) + ")")
                else:
                    print("found '" + ent.value + "' (" + str(ent.id) + ")")

            # add wikidata entry
            ent, created = Entities.objects.get_or_create(
                name=hit['unitLabel']['value'],
                repsys='wikidata',
                repsystem_id=7,
                quantity=quant,
                value=wdid,
                source='wikidata')
            ent.lastupdate = date.today()
            ent.save()
            if created:
                print("added '" + ent.value + "' (" + str(ent.id) + ")")
            else:
                print("found '" + ent.value + "' (" + str(ent.id) + ")")
        else:
            continue

# checked 1/13/23
if choice == 'runqudt':
    rsid = 10
    rdf = getrepsystemdata(rsid)
    g = Graph()
    g.parse(rdf.encode("utf-8"), format="json-ld")
    qudtunit = """
            PREFIX qk: <http://qudt.org/vocab/quantitykind/>
            PREFIX qudt: <http://qudt.org/schema/qudt/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX qudt: <http://qudt.org/schema/qudt/>
            PREFIX qk: <http://qudt.org/vocab/quantitykind/>

            SELECT * WHERE {
                ?unit   rdf:type qudt:Unit;
                        rdfs:label ?name;
                        qudt:hasQuantityKind ?type .
                OPTIONAL { ?unit qudt:symbol ?sym . }
                OPTIONAL { ?unit qudt:ucumCode ?ucum . }
                OPTIONAL { ?unit qudt:uneceCommonCode ?unece . }
                OPTIONAL { ?unit qudt:iec61360Code ?iec . }
                OPTIONAL { ?unit qudt:udunitsCode ?udu . }
                OPTIONAL { ?unit qudt:dbpediaMatch ?dbp . }
                OPTIONAL { ?unit qudt:omUnit ?oum2 . }
                FILTER (?type != qk:Currency)
            }
            ORDER BY ?name
            """

    units = g.query(qudtunit)
    for hit in units:
        repsyss = []
        if hit.ucum:
            repsyss.append({"name": "ucum", "rsid": 2})
        if hit.unece:
            repsyss.append({"name": "unece", "rsid": 6})
        if hit.iec:
            repsyss.append({"name": "iec", "rsid": 15})
        if hit.udu:
            repsyss.append({"name": "udu", "rsid": 14})
        if hit.dbp:
            repsyss.append({"name": "dbp", "rsid": 22})
        if hit.oum2:
            repsyss.append({"name": "oum2", "rsid": 13})

        for repsys in repsyss:
            repl = ''
            if 'dbpedia' in hit[repsys['name']]:
                repl = 'http://dbpedia.org/resource/'
            elif 'units-of-measure' in hit[repsys['name']]:
                repl = 'http://www.ontology-of-units-of-measure.org/resource/om-2/'
            ent, created = Entities.objects.get_or_create(
                name=hit.name,
                lang=hit.name.language,
                repsys=repsys['name'],
                repsystem_id=repsys['rsid'],
                symbol=hit.sym,
                quantity=hit.type.replace("http://qudt.org/vocab/quantitykind/", ""),
                value=hit[repsys['name']].replace(repl, ''),
                source='qudt')
            ent.lastupdate = date.today()
            ent.save()
            if created:
                print("added '" + str(ent.value) + "' (" + str(ent.id) + ")")
            else:
                print("found '" + str(ent.value) + "' (" + str(ent.id) + ")")
        # add the qudt representation
        ent, created = Entities.objects.get_or_create(
            name=hit.name,
            lang=hit.name.language,
            repsys="qudt",
            repsystem_id=10,
            symbol=hit.sym,
            quantity=hit.type.replace("http://qudt.org/vocab/quantitykind/", ""),
            value=hit.unit.replace("http://qudt.org/vocab/unit/", ""),
            source='qudt')
        ent.lastupdate = date.today()
        ent.save()
        if created:
            print("added '" + ent.value + "' (" + str(ent.id) + ")")
        else:
            print("found '" + ent.value + "' (" + str(ent.id) + ")")

# checked 1/12/23
if choice == 'runnerc':
    # raw file is the data file
    rsid = 16
    terms = getrepsystemdata(rsid)
    for term in terms["@graph"]:
        if term["@type"] == "skos:Concept":
            quant = None
            if 'broader' in term:
                down = None
                if isinstance(term['broader'], list):
                    for entry in term['broader']:
                        if 'nerc' in entry:
                            down = requests.get(entry + '?_profile=nvs&_mediatype=application/ld+json')
                elif isinstance(term['broader'], str):
                    if 'nerc' in term['broader']:
                        down = requests.get(term['broader'] + '?_profile=nvs&_mediatype=application/ld+json')
                if down:
                    broader = json.loads(down.content)
                    quant = broader['prefLabel']['@value']
            ent, created = Entities.objects.get_or_create(
                repsys='nerc',
                repsystem_id=rsid,
                name=term['prefLabel']['@value'],
                lang=term['prefLabel']['@language'],
                symbol=term['altLabel'],
                quantity=quant,
                value=term['@id'].replace('http://vocab.nerc.ac.uk/collection/P06/current/', '').replace('/', ''),
                source='nerc'
            )
            ent.save()
            if created:
                print("added '" + ent.value + "' (" + str(ent.id) + ")")
            else:
                print("found '" + ent.value + "' (" + str(ent.id) + ")")
            # find related representations
            if 'sameAs' in term:
                rep = None
                repsys = None
                rsid2 = None
                if isinstance(term['sameAs'], list):
                    for entry in term['sameAs']:
                        if 'qudt' in entry:
                            rep = entry.replace('http://qudt.org/vocab/unit/', '')
                            repsys = 'qudt'
                            rsid2 = 10
                        elif 'dbpedia' in entry:
                            rep = entry.replace('http://dbpedia.org/resource/', '')
                            repsys = 'dbpedia'
                            rsid2 = 17
                        if rep:
                            ent, created = Entities.objects.get_or_create(
                                repsys=repsys,
                                repsystem_id=rsid2,
                                name=term['prefLabel']['@value'],
                                lang=term['prefLabel']['@language'],
                                symbol=term['altLabel'],
                                quantity=quant,
                                value=rep,
                                source='nerc'
                            )
                            if created:
                                print("added '" + ent.value + "' (" + str(ent.id) + ")")
                            else:
                                print("found '" + ent.value + "' (" + str(ent.id) + ")")
                elif isinstance(term['sameAs'], str):
                    if 'qudt' in term['sameAs']:
                        repsys = 'qudt'
                        rsid2 = 10
                        rep = term['sameAs'].replace('http://qudt.org/vocab/unit/', '')
                    elif 'dbpedia' in term['sameAs']:
                        repsys = 'dbpedia'
                        rsid2 = 17
                        rep = term['sameAs'].replace('http://dbpedia.org/resource/', '')
                    if rep:
                        ent, created = Entities.objects.get_or_create(
                            repsys=repsys,
                            repsystem_id=rsid2,
                            name=term['prefLabel']['@value'],
                            lang=term['prefLabel']['@language'],
                            symbol=term['altLabel'],
                            quantity=quant,
                            value=rep,
                            source='nerc'
                        )
                        if created:
                            print("added '" + ent.value + "' (" + str(ent.id) + ")")
                        else:
                            print("found '" + ent.value + "' (" + str(ent.id) + ")")

# checked 1/12/23
if choice == 'rununece':
    # raw file is the data file
    rsid = 6
    units = getrepsystemdata(rsid)
    for unit in units["@graph"]:
        symbol = None
        if unit['uncefact:symbol'] != "":
            symbol = unit['uncefact:symbol']
        cmmt = {}
        cmmt.update({"category": unit['uncefact:levelCategory']})
        cmmt.update({"factor": unit['uncefact:conversionFactor']})
        cmmt.update({"status": unit['uncefact:status']})
        cmmt.update({"comment": unit['rdfs:comment']})
        ent, created = Entities.objects.get_or_create(
            repsys='unece',
            repsystem_id=rsid,
            name=unit['@id'].replace('rec20:', ''),
            lang='en',
            symbol=symbol,
            value=unit['rdf:value'],
            source='unece',
            comment=json.dumps(cmmt)
        )
        ent.save()
        if created:
            print("added '" + ent.value + "' (" + str(ent.id) + ")")
        else:
            print("found '" + ent.value + "' (" + str(ent.id) + ")")
        print(unit)

# checked 1/12/23
if choice == 'runsweet':
    # raw file is the data file
    rsid = 5
    units = getrepsystemdata(rsid)
    for unit in units["@graph"]:
        if 'sameAs' in unit or 'notation' not in unit:
            continue
        if isinstance(unit['@type'], list):
            types = ' '.join(unit['@type'])
            if 'Unit' not in types:
                continue
            cmmt = {}
            if 'hasBaseUnit' in unit:
                cmmt.update({"baseunit": unit['hasBaseUnit']})
            if 'sorelm:hasScalingNumber' in unit:
                cmmt.update({"factor": unit['sorelm:hasScalingNumber']})
            ent, created = Entities.objects.get_or_create(
                repsys='sweet',
                repsystem_id=rsid,
                name=unit['label']['@value'],
                lang=unit['label']['@language'],
                value=unit['notation'],
                source='sweet',
                comment=json.dumps(cmmt)
            )
            ent.save()
            if created:
                print("added '" + str(ent.value) + "' (" + str(ent.id) + ")")
            else:
                print("found '" + str(ent.value) + "' (" + str(ent.id) + ")")

# checked 1/12/23
if choice == 'runuo':
    rsid = 8
    data = getrepsystemdata(rsid)
    for unit in data:
        types = ':'.join(unit['@type'])
        if types == 'http://www.w3.org/2002/07/owl#NamedIndividual:http://www.w3.org/2002/07/owl#Class':
            value = unit['@id'].replace("http://purl.obolibrary.org/obo/", "")
            cmmt = unit['http://www.w3.org/2000/01/rdf-schema#comment'][0]['@value']
            name = unit['http://www.w3.org/2000/01/rdf-schema#label'][0]['@value']
            symbol = None
            if 'oboInOwl:hasExactSynonym' in unit:
                for val in unit['oboInOwl:hasExactSynonym']:  # chooses the shortest length string as
                    if not symbol:
                        symbol = val['@value']
                    elif len(val['@value']) < len(symbol):
                        symbol = val['@value']
            ent, created = Entities.objects.get_or_create(
                repsys='uo',
                repsystem_id=rsid,
                name=name,
                lang='en',
                symbol=symbol,
                value=value,
                source='uo',
                comment=cmmt
            )
            ent.save()
            if created:
                print("added '" + str(ent.value) + "' (" + str(ent.id) + ")")
            else:
                print("found '" + str(ent.value) + "' (" + str(ent.id) + ")")

# checked 1/12/23
if choice == 'runncit':
    rsid = 9
    units = getrepsystemdata(rsid)
    for unit in units:
        ent, created = Entities.objects.get_or_create(
            repsys='ncit',
            repsystem_id=rsid,
            name=unit['name'],
            symbol=unit['symbol'],
            quantity=unit['quantity'],
            lang='en',
            value=unit['value'],
            source='ncit',
            comment=unit['description']
        )
        ent.lastupdate = date.today()
        ent.save()
        if created:
            print("added '" + str(ent.value) + "' (" + str(ent.id) + ")")
        else:
            print("found '" + str(ent.value) + "' (" + str(ent.id) + ")")

# checked 1/12/23
if choice == 'rununitsml':
    rsid = 19
    units = getrepsystemdata(rsid)
    for unit in units:
        ent, created = Entities.objects.get_or_create(
            repsys='unitsml',
            repsystem_id=rsid,
            name=unit['name'],
            symbol=unit['symbol'],
            quantity=unit['quantity'],
            quantityid=unit['quantityids'],
            lang='en',
            value=unit['code'],
            source='unitsml',
            comment=unit['type']
        )
        ent.lastupdate = date.today()
        ent.save()
        if created:
            print("added '" + str(ent.value) + "' (" + str(ent.id) + ")")
        else:
            print("found '" + str(ent.value) + "' (" + str(ent.id) + ")")

# checked 1/13/23
if choice == 'rungb':
    rsid = 3
    units = getrepsystemdata(rsid)
    for unit in units:
        ent, created = Entities.objects.get_or_create(
            repsys='igb',
            repsystem_id=rsid,
            name=unit['name'],
            lang='en',
            value=unit['code'],
            source='igb',
            comment=unit['defn']
        )
        ent.lastupdate = date.today()
        ent.save()
        if created:
            print("added '" + str(ent.value) + "' (" + str(ent.id) + ")")
        else:
            print("found '" + str(ent.value) + "' (" + str(ent.id) + ")")
