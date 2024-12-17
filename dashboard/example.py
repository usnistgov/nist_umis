# import json
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "umisconfig.settings")
django.setup()
from dashboard.repsys_ingest import *
from datetime import date
from units.functions import *
from wdfunctions import *

choice = 'wdc'

local = timezone("America/New_York")

# checked 6/17/24 (List of Units not available, falling back to files from 4/25/23)
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

# checked 6/17/24
if choice == 'runwd':
    # load current file
    rsid = 7
    data = getrepsystemdata(rsid)
    hits = json.loads(data)
    flds = ['iev', 'igb', 'ncit', 'qudt', 'ucum', 'unece', 'uom', 'wolf', 'wur']
    # analyze data to remove entries that have SI unit (or equivalent) as quantity
    cnt = 0
    for hit in hits['results']['bindings']:
        # print(hit)
        # exit()
        # add wikidata entry
        found = Wdunits.objects.filter(uurl__exact=hit['u']['value'])
        if not found:
            keys = hit.keys()
            # print(keys)
            for fld in flds:
                if fld not in keys:
                    hit.update({fld: {"value": None}})
            wu = Wdunits(
                cls=hit['cls']['value'],
                unit=hit['unit']['value'],
                quantity=hit['quant']['value'],
                curl=hit['c']['value'],
                uurl=hit['u']['value'],
                qurl=hit['q']['value'],
                iev=hit['iev']['value'],
                igb=hit['igb']['value'],
                ncit=hit['ncit']['value'],
                qudt=hit['qudt']['value'],
                ucum=hit['ucum']['value'],
                unece=hit['unece']['value'],
                uom=hit['uom2']['value'],
                wolf=hit['wolf']['value'],
                wur=hit['wur']['value'],
                added=date.today(),
                updated=local.localize(datetime.now())
            )
            wu.save()
            print("added '" + wu.unit + "' (" + str(wu.id) + ")")
            cnt += 1
            if cnt == 10:
                exit()
        else:
            # check for data and add if the field is empty
            f = found[0]
            for fld in flds:
                if fld in hit.keys() and getattr(f, fld) is None:
                    setattr(f, fld, hit.get(fld)['value'])
                    f.save()
                    print("field " + fld + " updated for unit " + f.unit)
                    exit()
            print("found unit '" + f.unit + "'")
        continue

# checked 6/11/24
if choice == 'runqudt':
    rsid = 10
    rdf = getrepsystemdata(rsid)
    g = Graph()
    g.parse(rdf.encode("utf-8")).serialize(format="json-ld")
    qudtunit = """
            PREFIX qk: <http://qudt.org/vocab/quantitykind/>
            PREFIX qudt: <http://qudt.org/schema/qudt/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX qudt: <http://qudt.org/schema/qudt/>
            PREFIX qk: <http://qudt.org/vocab/quantitykind/>

            SELECT ?unit ?name ?type ?sym ?ucum ?unece ?iec ?udu ?dbp ?uom2 WHERE {
                ?unit   rdf:type qudt:Unit;
                        rdfs:label ?name .
                OPTIONAL { ?unit qudt:hasQuantityKind ?type . }
                OPTIONAL { ?unit qudt:symbol ?sym . }
                OPTIONAL { ?unit qudt:ucumCode ?ucum . }
                OPTIONAL { ?unit qudt:uneceCommonCode ?unece . }
                OPTIONAL { ?unit qudt:iec61360Code ?iec . }
                OPTIONAL { ?unit qudt:udunitsCode ?udu . }
                OPTIONAL { ?unit qudt:dbpediaMatch ?dbp . }
                OPTIONAL { ?unit qudt:omUnit ?uom2 . }
            }
            ORDER BY ?name
            """

    units = g.query(qudtunit)
    for hit in units:
        if hit.type is not None and 'Currency' in hit.type:
            continue
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
        if hit.uom2:
            repsyss.append({"name": "uom2", "rsid": 13})

        # process the other unit system representations
        for repsys in repsyss:
            repl = ''
            if 'dbpedia' in hit[repsys['name']]:
                repl = 'http://dbpedia.org/resource/'
            elif 'units-of-measure' in hit[repsys['name']]:
                repl = 'http://www.ontology-of-units-of-measure.org/resource/om-2/'
            if hit.type is not None:
                hit.type = hit.type.replace("http://qudt.org/vocab/quantitykind/", "")
            ent, created = Entities.objects.get_or_create(
                name=hit.name,
                lang=hit.name.language,
                repsys=repsys['name'],
                repsystem_id=repsys['rsid'],
                symbol=hit.sym,
                quantity=hit.type,
                value=hit[repsys['name']].replace(repl, ''),
                source='qudt')
            if ent.migrated == 'yes':
                # don't reset migrated to 'no'!
                print(hit)
            else:
                ent.migrated = 'no'
            ent.lastcheck = date.today()
            ent.updated = getds()
            ent.save()
            if created:
                print("added '" + str(ent.value) + "' (" + str(ent.id) + ")")
            else:
                print("found '" + str(ent.value) + "' (" + str(ent.id) + ")")

        # add the qudt representation
        if hit.type is not None:
            hit.type = hit.type.replace("http://qudt.org/vocab/quantitykind/", "")
        ent, created = Entities.objects.get_or_create(
            name=hit.name,
            lang=hit.name.language,
            repsys="qudt",
            repsystem_id=10,
            symbol=hit.sym,
            quantity=hit.type,
            value=hit.unit.replace("http://qudt.org/vocab/unit/", ""),
            source='qudt')
        if ent.migrated == 'yes':
            # don't reset migrated to 'no'!
            print(hit)
        else:
            ent.migrated = 'no'
        ent.lastcheck = date.today()
        ent.updated = getds()
        ent.save()
        if created:
            print("added '" + ent.value + "' (" + str(ent.id) + ")")
        else:
            print("found '" + ent.value + "' (" + str(ent.id) + ")")

# checked 6/11/24
if choice == 'runnerc':
    # raw file is the data file
    rsid = 16
    jsn = getrepsystemdata(rsid)
    units = json.loads(jsn)
    for term in units["@graph"]:
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
                value=term['@id'].replace('https://vocab.nerc.ac.uk/collection/P06/current/', '').replace('/', ''),
                source='nerc'
            )
            if ent.migrated == 'yes':
                # don't reset migrated to 'no'!
                print(term)
            else:
                ent.migrated = 'no'
            ent.lastcheck = date.today()
            ent.updated = getds()
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
                            repsys = 'dbp'
                            rsid2 = 22
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
                            if ent.migrated == 'yes':
                                # don't reset migrated to 'no'!
                                print(term)
                            else:
                                ent.migrated = 'no'
                            ent.lastcheck = date.today()
                            ent.updated = getds()
                            ent.save()
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
                        repsys = 'dbp'
                        rsid2 = 22
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
                        if ent.migrated == 'yes':
                            # don't reset migrated to 'no'!
                            print(term)
                        else:
                            ent.migrated = 'no'
                        ent.lastcheck = date.today()
                        ent.updated = getds()
                        ent.save()
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

# checked 6/11/24 (ttl file (direct URL) imports as JSON-LD, how?)
if choice == 'runsweet':
    # raw file is the data file
    rsid = 5
    jsn = getrepsystemdata(rsid)
    units = json.loads(jsn)
    for unit in units["@graph"]:
        if 'sameAs' in unit or 'notation' not in unit:
            continue

        if isinstance(unit['@type'], list):
            types = ' '.join(unit['@type'])
            if 'Unit' not in types:
                continue

            # print(json.dumps(unit, indent=4))
            # exit()
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
                source='sweet'
            )
            ent.comment = json.dumps(cmmt)
            ent.lastcheck = date.today()
            ent.updated = getds()
            ent.save()
            if created:
                print("added '" + str(ent.value) + "' (" + str(ent.id) + ")")
                exit()
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
        ent.lastcheck = date.today()
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
        ent.lastucheck = date.today()
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
        ent.lastcheck = date.today()
        ent.save()
        if created:
            print("added '" + str(ent.value) + "' (" + str(ent.id) + ")")
        else:
            print("found '" + str(ent.value) + "' (" + str(ent.id) + ")")

# checked 1/28/23
if choice == 'runucum':
    # read the units data file and add the units to the entities table
    rsid = 2
    data = getrepsystemdata(rsid)
    units = data['units']['data']
    for unit in units:
        # case-sensitive (index 2 in json array)
        if unit[16] is None:
            unit[16] = ""
        if unit[18] is None:
            unit[18] = ""
        if unit[19] is None:
            unit[19] = ""
        if unit[20] is None:
            unit[20] = ""

        ent, created = Entities.objects.get_or_create(
            repsys='ucum',
            repsystem_id=rsid,
            name=unit[1],
            lang='en',
            value=unit[2],
            source='ucum',
            comment='{"LOINC property": "' + unit[18] + '", "synonyms": "' + unit[16] +
                    '", "category": "' + unit[19] + '", "guidance": "' + unit[20] + '"}'
        )
        ent.lastcheck = date.today()
        ent.save()
        if created:
            print("added '" + str(ent.value) + "' (" + str(ent.id) + ")")
        else:
            print("found '" + str(ent.value) + "' (" + str(ent.id) + ")")
        # case-insensitive (index 3 in json array)
        ent, created = Entities.objects.get_or_create(
            repsys='ucum',
            repsystem_id=rsid,
            name=unit[1],
            lang='en',
            value=unit[3],
            source='ucum',
            comment='{"LOINC property": "' + unit[18] + '", "synonyms": "' + unit[16] +
                    '", "category": "' + unit[19] + '", "guidance": "' + unit[20] + '"}'
        )
        ent.lastcheck = date.today()
        ent.save()
        if created:
            print("added '" + str(ent.value) + "' (" + str(ent.id) + ")")
        else:
            print("found '" + str(ent.value) + "' (" + str(ent.id) + ")")

# get list of unit of measurement subclasses on Wikidata
if choice == 'wdc':
    classes = wdclasses()  # call class to update if working on wikidata OR download from wd and parse below
    # print(classes)
    # exit()

    # classes = None
    # file = f'umis_quants_query_111424.json'
    # if os.path.exists(os.path.join(BASE_DIR, STATIC_URL, file)):
    #     # read in the file
    #     with open(os.path.join(BASE_DIR, STATIC_URL, file), 'r') as f:
    #         tmp = f.read()
    #         classes = json.loads(tmp)
    #         f.close()
    # exit()

    for cls in classes:
        if not isinstance(cls['class'], str):
            cls['class'] = cls['class']['value']
        if not isinstance(cls['c'], str):
            cls['c'] = cls['c']['value']
        if not isinstance(cls['isq'], str):
            cls['isq'] = cls['isq']['value']
        if not isinstance(cls['src'], str):
            cls['src'] = cls['src']['value']
        if not isinstance(cls['sect'], str):
            cls['sect'] = cls['sect']['value']
        if not isinstance(cls['quant'], str):
            cls['quant'] = cls['quant']['value']

        tmp = re.findall(r'alttext="\{(.+?)}"', cls['isq'])
        isq = (tmp[0].replace("\\displaystyle", '').replace("\\mathsf", '').replace(' ', '').
               replace('{{', '').replace('}}', ''))
        cls['isq'] = isq
        # ignore classes that have multiple related quantities
        if cls['class'] in ['unit of molar energy']:
            continue
        # get quantity ID
        quant = Quantities.objects.filter(iso_item=cls['sect'])
        qid = None
        if quant:
            q = quant[0]
            qid = q.id
        else:
            print("can't find quantity with section " + cls['sect]'])
            exit()
        # add or update Wdclasses table
        c, created = Wdclasses.objects.get_or_create(
            name=cls['class'], url=cls['c'], isq=cls['isq'], source=cls['src'], section=cls['sect'],
            quant=cls['quant'], quantity_id=qid
        )
        c.save()
        if created:
            c.updated = local.localize(datetime.now())
            c.save()
            print("added class '" + str(c.name) + "'")
        else:
            if not c.quantity_id:
                quant = Quantities.objects.filter(iso_item=cls['sect'])
                if quant:
                    q = quant[0]
                    c.quantity_id = q.id
                    c.save()
                else:
                    print("can't find quantity with section " + cls['sect]'])
                    exit()
                print("updated class '" + str(c.name) + "'")
            else:
                print("found class '" + str(c.name) + "'")
    exit()

# get list of units on Wikidata
# get list of units on Wikidata
if choice == 'wdu':
    # units = wdunits()  # call class to update wdunits if working on wikidata OR download from wd and parse below
    # query to server not working currently (11/14/24)

    # define variables
    repsysids = {"qudt": 10, "iev": 21, "igb": 3, "ncit": 9, "ucum": 2, "unece": 6, "uom": 13, "wolf": 20, "wur": 23}

    units = None
    file = f'umis_units_query_121724.json'
    if os.path.exists(os.path.join(BASE_DIR, STATIC_URL, file)):
        # read in the file (open function has read as default so not added)
        with open(os.path.join(BASE_DIR, STATIC_URL, file)) as f:
            tmp = f.read()
            units = json.loads(tmp)
            f.close()

    cnt = 0
    for unit in units:
        # add/update wikidata entry
        flds = ['curl', 'cls', 'uurl', 'unit', 'qurl', 'quant', 'factor', 'iev', 'igb', 'ncit',
                'qudt', 'ucum', 'unece', 'uom', 'wolf', 'wur']
        uflds = ['iev', 'igb', 'ncit', 'qudt', 'ucum', 'unece', 'uom', 'wolf', 'wur']
        dt = local.localize(datetime.now())
        if not isinstance(unit['uurl'], str):
            found = Wdunits.objects.filter(uurl__exact=unit['uurl']['value'])
        else:
            found = Wdunits.objects.filter(uurl__exact=unit['uurl'])

        # add unit if not found
        if not found:
            # convert fields to be consistent across sources
            keys = unit.keys()
            for fld in flds:
                if fld not in keys:
                    # only via qwikidata are fields not set
                    unit.update({fld: None})
                if not isinstance(fld, str):
                    setattr(unit, fld, getattr(unit, fld))

            # add unit
            wu = Wdunits(cls=unit['cls'], unit=unit['unit'], quant=unit['quant'], factor=unit['factor'],
                         curl=unit['curl'], uurl=unit['uurl'], qurl=unit['qurl'], added=date.today(), updated=dt
                         )
            print("added")
        else:
            # check for unit representation data and add if the field is empty
            wu = found[0]
            print("found")

        # if missing add wd unit class if available
        if not wu.wdclass_id:
            cls = Wdclasses.objects.filter(url__exact=unit['curl'])
            if cls:
                wu.wdclass_id = cls[0].id

        # save to wdunits table
        wu.save()

        # add any unit reps to the representations table
        for ufld in uflds:
            repsysid, strng = None, None
            if ufld in unit.keys():
                # find (or add) unit string in the strng table
                strng = Strngs.objects.get(string=unit[ufld])
                if not strng:
                    # add new unit string
                    strng = Strngs(string=unit[ufld], status='current', autoadded='yes', updated=dt)

                repsysid = repsysids[ufld]
                rep = Representations.objects.get(repsystem__id=repsysid, strng_id=strng.id)
                if rep:
                    if rep.wdunit_id and rep.onwd == "yes":
                        print("representation " + unit[ufld] + " already added")
                        continue
                    print(rep.__dict__)
                    print(unit)
                    exit()

                    # update representation entry with wdunit_id
                    rep.wdunit_id = wu.id
                    rep.onwd = 'yes'
                    rep.save()
                else:
                    # add representation entry
                    urlep = 'no'
                    if ufld in ["qudt", "iev", "igb", "ncit", "uom"]:
                        urlep = 'yes'
                    newrep = Representations(wdunit_id=wu.id, repsystem_id=repsysid, strng_id=strng.id,
                                             url_endpoint=urlep, status='current', onwd='yes', checked='no', updated=dt)
                    newrep.save()

        print("added '" + wu.unit + "' (" + str(wu.id) + ")")
        cnt += 1
        if cnt > 4:
            exit()


# get a list of quantities on wikidata
if choice == 'wdq':
    quants = wdquants()  # call class to update wdquants if working on wikidata OR download from wd and parse below

    cnt = 0
    for q in quants:
        quant = {}
        keys = q.keys()
        if not isinstance(q['qntid'], str):
            quant['qurl'] = q['qntid']['value']
        if not isinstance(q['quant'], str):
            quant['name'] = q['quant']['value']
        if 'source' in keys and not isinstance(q['source'], str):
            quant['source'] = q['source']['value']
        else:
            quant['source'] = None
        if 'sect' in keys and not isinstance(q['sect'], str):
            quant['sect'] = q['sect']['value']
        else:
            quant['sect'] = None
        if 'isq' in keys:
            isq = q['isq']['value']
            if 'merror' in isq:
                quant['isq'] = None
            else:
                tmp = re.findall(r'alttext="\{(.+?)}"', isq)
                isq = (tmp[0].replace("\\displaystyle", '').replace("\\mathsf", '').replace(' ', '').
                       replace('{{', '').replace('}}', ''))
                quant['isq'] = isq
        else:
            quant['isq'] = None
        qnt = None
        if quant['source'] and quant['sect']:
            num = re.findall(r'([A-Z]{3}) 80000-(\d+?):', str(quant['source']))
            isocode = num[0][0] + '-80000-' + num[0][1]
            # search the quantities table for quantity based on the source and section
            found = Quantities.objects.filter(iso_source=isocode, iso_item=quant['sect'])
            if found:
                qnt = found[0]
            else:
                # search by quantity name
                found = Quantities.objects.filter(name=quant['name'])
                if found:
                    qnt = found[0]

        # check if quantity already added
        add, created = Wdquants.objects.get_or_create(
            quant=qnt,
            qurl=quant['qurl'],
            name=quant['name'],
            source=quant['source'],
            sect=quant['sect'],
            isq=quant['isq']
        )
        add.save()

        if created:
            add.updated = local.localize(datetime.now())
            add.save()
            print("added '" + add.name + "' (" + str(add.id) + ")")
            # print(quant)
        else:
            print("already added " + quant['name'])

# check wdquants data against the quantities data
if choice == 'wdqchk':
    qs = Wdquants.objects.all().values('quant', 'sect')
    for q in qs:
        if q['quant'] and q['sect']:
            found = Quantities.objects.filter(id=q['quant'], iso_item=q['sect'])
            if not found:
                print(q)
                exit()
