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


choice = 'runncit'

if choice == 'getiec':
    # get the data in the IEC CDD and save it as files for quantities and units
    rsid = 15
    repsysobj = Repsystems.objects.get(id=rsid)
    repsys = Repsystems.objects.values('id', 'url', 'fileupdated').get(id=rsid)
    # starting with the list of units page (below) go out to all the quantities and record the units they point too
    url = repsys['url']
    html = requests.get(url)
    data = BeautifulSoup(html.content, "html.parser")
    quants = data.select("a[href*=OpenDocument]")
    qout, uout = [], []
    for quant in quants:
        code = quant.text
        if 'UAD' not in code:  # UAD entries are quantities
            continue
        qurl = quant['href']
        qurl = qurl.replace('?opendocument', '')
        qname = quant.parent.nextSibling.text
        qout.append({'name': qname, 'code': code, 'url': qurl})
        # go to the quant page to get the units...
        qhtml = requests.get('https://cdd.iec.ch' + qurl)
        qdata = BeautifulSoup(qhtml.content, "html.parser")
        units = qdata.find(string=re.compile("Codes of units:")).parent.next_sibling.find_all('a')
        for unit in units:
            uurl = unit['href']
            uurl = uurl.replace('?opendocument', '')
            text = unit.text
            code, name = text.split(' - ')
            uhtml = requests.get('https://cdd.iec.ch' + uurl)
            upage = BeautifulSoup(uhtml.content, "html.parser")
            tbl = upage.find(id="contentL1")
            udata = {}
            for row in tbl.find_all('tr'):
                cells = row.find_all('td')
                name = cells[0].text.strip('\n :')
                value = cells[1].text.strip('\n ')
                udata.update({name: value})
            uout.append({'name': udata['Preferred name'], 'code': code, 'url': uurl, 'shortname': udata['Short name'],
                         'definition': udata['Definition'], 'unece': udata['Remark'].replace('UN/ECE code: ', ''),
                         'quantity': qname, 'quanturl': qurl})
    # write out the files
    jqout = json.dumps(qout)
    with open(os.path.join(BASE_DIR, STATIC_URL, f'repsys_{rsid}_quants.json'), 'w') as f:
        f.write(jqout)
        f.close()
    juout = json.dumps(uout)
    with open(os.path.join(BASE_DIR, STATIC_URL, f'repsys_{rsid}_units.json'), 'w') as f:
        f.write(juout)
        f.close()
    # update the DB record
    rdate = datetime.strptime(html.headers['Last-Modified'], '%a, %d %b %Y %H:%M:%S %Z').date()
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
    exit()

if choice == 'runiec':
    # read the units data file and add the units to the entities table
    rsid = 15
    with open(os.path.join(BASE_DIR, STATIC_URL, f'repsys_{rsid}_units.json'), 'r') as f:
        tmp = f.read()
        f.close()
    units = json.loads(tmp)
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

if choice == 'runwd':
    # load current file
    rsid = 7
    data = getrepsystemdata(rsid)
    for hit in data['results']['bindings']:
        # check the hits for any that are not useful
        if "http://www.wikidata.org/entity/Q" not in hit['unit']['value']:
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

if choice == 'runqudt':
    rsid = 10
    repsys = Repsystems.objects.values('id', 'url', 'fileupdated').get(id=rsid)
    # getrepsystemdata(rsid)  # converts the ttl file into jsonld (when .ttl file updated)
    # TODO: run update when todays date of ttl file is more recent than that of the json file
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

if choice == 'runnerc':
    rsid = 16
    repsys = Repsystems.objects.values('id', 'url', 'fileupdated').get(id=rsid)
    with open(os.path.join(BASE_DIR, STATIC_URL, f'repsys_{rsid}_data.json'), 'r') as f:
        tmp = f.read()
        f.close()
    terms = json.loads(tmp)
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

if choice == 'rununece':
    rsid = 6
    repsys = Repsystems.objects.values('id', 'url', 'fileupdated').get(id=rsid)
    with open(os.path.join(BASE_DIR, STATIC_URL, f'repsys_{rsid}_data.json'), 'r') as f:
        tmp = f.read()
        f.close()
    units = json.loads(tmp)
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

if choice == 'runsweet':
    rsid = 5
    repsys = Repsystems.objects.values('id', 'url', 'fileupdated').get(id=rsid)
    with open(os.path.join(BASE_DIR, STATIC_URL, f'repsys_{rsid}_data.json'), 'r') as f:
        tmp = f.read()
        f.close()
    units = json.loads(tmp)
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

if choice == 'runuo':
    rsid = 8
    jdata = getrepsystemdata(rsid)
    data = json.loads(jdata)
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

if choice == 'runncit':
    rsid = 9
    jdata = getrepsystemdata(rsid)
    print(jdata)
    exit()
