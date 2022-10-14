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

if choice == 'runiec':
    rsid = 15
    repsysobj = Repsystems.objects.get(id=rsid)
    repsys = Repsystems.objects.values('id', 'url', 'fileupdated').get(id=rsid)
    # check if URL is valid
    req = requests.get(repsys['url'])
    if req.status_code != 200:
        print('invalid request!')
    typechar = req.headers['Content-type']
    parts = typechar.split("; ")
    ext = mimetypes.guess_extension(parts[0], )
    # TODO: add check for existing file and comparison of bytes
    with open(os.path.join(BASE_DIR, STATIC_URL, f'repsys_{rsid}{ext}'), 'wb') as f:
        f.write(req.content)
        f.close()
    # check for file update -> format of req['Last-Modified'] is "Mon, 10 Oct 2022 20:32:55 GMT"
    rdate = datetime.strptime(req.headers['Last-Modified'], '%a, %d %b %Y %H:%M:%S %Z').date()
    ldate = repsys['fileupdated']

    if ldate is None:
        repsysobj.fileupdated = rdate
        print('added file last modified date')
    elif ldate < rdate:
        repsysobj.fileupdated = rdate
        print('file has been updated')
    else:
        print('file unchanged')
    pyjax = pytz.timezone("America/New_York")
    repsysobj.checked = pyjax.localize(datetime.now())
    repsysobj.save()

if choice == 'runwd':
    # load current file
    rsid = 7
    repsys = Repsystems.objects.values('id', 'url', 'fileupdated').get(id=rsid)
    with open(os.path.join(BASE_DIR, STATIC_URL, f'repsys_{rsid}_data.json'), 'r') as f:
        tmp = f.read()
        f.close()
    data = json.loads(tmp)
    for hit in data['results']['bindings']:
        if "http://www.wikidata.org/entity/Q" not in hit['unit']['value']:
            # russian entries
            continue
        wdid = hit['unit']['value'].replace("http://www.wikidata.org/entity/", "")
        # disabled so we capture this data that is mostly ucum codes...
        # if wdid == hit['unitLabel']['value']:
        #     # entries where name is not defined
        #     continue
        #     print(hit)
        if ('qudt' or 'ncit' or 'ucum' or 'unece' or 'uom2' or 'iec' or 'wolf' or 'iev') in hit:
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
                repsyss.append({'name': "uom2", 'rsid': 10})
            if 'iec' in hit:
                repsyss.append({'name': "iec", 'rsid': 10})
            if 'wolf' in hit:
                repsyss.append({'name': "wolf", 'rsid': 10})
            if 'iev' in hit:
                repsyss.append({'name': "iev", 'rsid': 10})
            for repsys in repsyss:
                ent, created = Entities.objects.get_or_create(
                    name=hit['unitLabel']['value'],
                    repsys=repsys['name'],
                    repsystem_id=repsys['rsid'],
                    quantity=hit['subclassLabel']['value'].replace("unit of", ""),
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
                quantity=hit['subclassLabel']['value'].replace("unit of", ""),
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
    exit()

if choice == 'runqudt':
    rsid = 10
    repsys = Repsystems.objects.values('id', 'url', 'fileupdated').get(id=rsid)
    with open(os.path.join(BASE_DIR, STATIC_URL, f'repsys_{rsid}_data.json'), 'r') as f:
        tmp = f.read()
        f.close()
    # process as RDF
    g = Graph()
    g.parse(tmp.encode("utf-8"), format="json-ld")
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

        for repsys in repsyss:
            ent, created = Entities.objects.get_or_create(
                name=hit.name,
                lang=hit.name.language,
                repsys=repsys['name'],
                repsystem_id=repsys['rsid'],
                symbol=hit.sym,
                quantity=hit.type.replace("http://qudt.org/vocab/quantitykind/", ""),
                value=hit[repsys['name']],
                source='qudt')
            ent.lastupdate = date.today()
            ent.save()
            if created:
                print("added '" + ent.value + "' (" + str(ent.id) + ")")
            else:
                print("found '" + ent.value + "' (" + str(ent.id) + ")")
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
