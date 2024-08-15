from rdflib import Graph
import os
import django
import requests

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "umisconfig.settings")
django.setup()
from unitsystems.models import *
from datetime import datetime
from pylatexenc.latex2text import LatexNodes2Text
from pytz import timezone

jax = timezone("America/New_York")


def ingestunits():
    """ download the latest qudt ttl file and load into the database """
    url = 'https://raw.githubusercontent.com/qudt/qudt-public-repo/main/vocab/unit/VOCAB_QUDT-UNITS-ALL-v2.1.ttl'
    resp = requests.get(url)
    rdf = resp.text
    g = Graph()
    g.parse(rdf.encode("utf-8")).serialize(format="json-ld")
    qudtunit = """
            PREFIX qk: <http://qudt.org/vocab/quantitykind/>
            PREFIX qudt: <http://qudt.org/schema/qudt/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX qudt: <http://qudt.org/schema/qudt/>
            PREFIX qk: <http://qudt.org/vocab/quantitykind/>

            SELECT ?unit ?name ?siex ?vec ?mult ?defu ?defc ?defs ?sym ?desc ?iso ?alt ?tex ?udu ?dbp ?uom2
                (group_concat(?sys) as ?syss) (group_concat(?kind) as ?kinds) (group_concat(?iec) as ?iecs) 
                (group_concat(?ucum) as ?ucums) (group_concat(?unec) as ?unecs) (group_concat(?inf) as ?infs) WHERE {
                ?unit   rdf:type qudt:Unit;
                        rdfs:label ?name .
                OPTIONAL { ?unit qudt:siExactMatch ?siex . }
                OPTIONAL { ?unit qudt:applicableSystem ?sys . }
                OPTIONAL { ?unit qudt:hasDimensionVector ?vec . }
                OPTIONAL { ?unit qudt:hasQuantityKind ?kind . }
                OPTIONAL { ?unit qudt:conversionMultiplier ?mult . }
                OPTIONAL { ?unit qudt:definedUnitOfSystem ?defu . }
                OPTIONAL { ?unit qudt:derivedCoherentUnitOfSystem ?defc . }
                OPTIONAL { ?unit qudt:derivedUnitOfSystem ?defs . }
                OPTIONAL { ?unit qudt:isoNormativeReference ?iso . }
                OPTIONAL { ?unit qudt:informativeReference ?inf . }
                OPTIONAL { ?unit dcterms:description ?desc . }
                OPTIONAL { ?unit qudt:symbol ?sym . }
                OPTIONAL { ?unit skos:altLabel ?alt . }
                OPTIONAL { ?unit qudt:latexDefinition ?tex . }
                OPTIONAL { ?unit qudt:ucumCode ?ucum . }
                OPTIONAL { ?unit qudt:uneceCommonCode ?unec . }
                OPTIONAL { ?unit qudt:iec61360Code ?iec . }
                OPTIONAL { ?unit qudt:udunitsCode ?udu . }
                OPTIONAL { ?unit qudt:dbpediaMatch ?dbp . }
                OPTIONAL { ?unit qudt:omUnit ?uom2 . }
                FILTER(LANG(?name) = "en")
            }
            GROUP BY ?unit ?name ?siex ?vec ?mult ?defu ?defc ?defs ?sym ?desc ?iso ?alt ?tex ?udu ?dbp ?uom2
            """
    # quantitykind data for use in for loop below
    tmp = Qudtqkinds.objects.all().values('id', 'code')
    qkinds = {}
    for i in tmp:
        qkinds.update({i['code']: i['id']})
    # unitsystem data for use in for loop below
    tmp = Unitsystems.objects.all().values('id', 'abbrev')
    usyss = {}
    for i in tmp:
        usyss.update({i['abbrev']: i['id']})
    # run query
    units = g.query(qudtunit)
    for hit in units:
        code = hit.unit.replace('http://qudt.org/vocab/unit/', '')
        print("**starting " + code + "**")
        foundall = Qudtunits.objects.filter(code=code)
        if foundall:
            found = foundall[0]
            if not found.name and hit.name:
                # label@en
                found.name = hit.name
                print("added name")
            else:
                print("unit " + hit.name + " up to date")
                continue  # assume if name present then it has been updated...
            if not found.dimvector and hit.vec:
                # hasDimensionVector
                found.dimvector = hit.vec.replace('http://qudt.org/vocab/dimensionvector/', '')
                print("added dimension vector")
            # QUDT quantitykinds <-> QUDT units join table
            if hit.kinds:
                kinds = list(set(hit.kinds.split(' ')))  # not sure why there are duplicates sometimes
                # check that updates are needed
                if len(found.qudtqkindsqudtunits_set.all()) != len(kinds):
                    ccnt = 0
                    codes = (QudtqkindsQudtunits.objects.filter(qudtunit_id=found.id).
                             values_list('qudtqkind__code', flat=True))
                    ns = 'http://qudt.org/vocab/quantitykind/'
                    # update join table
                    joinqkqu(found, kinds, qkinds, ccnt, ns, codes)
                    # check for joins that need to be removed
                    if ccnt == 0:
                        klist = []
                        for kind in kinds:
                            klist.append(kind.replace(ns, ''))
                        diffs = list(set(codes) - set(klist))
                        for diff in diffs:
                            qkind = Qudtqkinds.objects.get(code=diff)
                            join = QudtqkindsQudtunits.objects.get(qudtqkind_id=qkind.id, qudtunit_id=found.id)
                            join.delete()
                            print('deleted quantitykind ' + diff + " from unit '" + hit.name + "' (correct?)")
            # quantity systems <-> QUDT units join table
            if hit.syss:
                syss = list(set(hit.syss.split(' ')))  # not sure why there are duplicates sometimes
                # check that updates are needed
                if len(found.unitsystemsqudtunits_set.all()) != len(syss):
                    ucnt = 0
                    abbs = (UnitsystemsQudtunits.objects.filter(qudtunit_id=found.id).
                            values_list('unitsystem__abbrev', flat=True))
                    ns = 'http://qudt.org/vocab/sou/'
                    # update join table
                    joinusqu(found, syss, usyss, ucnt, ns, abbs)
                    # check for joins that need to be removed
                    if ucnt == 0 and abbs:
                        slist = []
                        for sys in syss:
                            slist.append(sys.replace(ns, ''))
                        diffs = list(set(syss) - set(slist))
                        print(diffs)
                        print("write code!")
                        exit()
            # check other fields
            if not found.siexact and hit.siex:
                # siExactMatch 43
                match = hit.siex.replace('https://si-digital-framework.org/SI/units/', '')
                found.siexact = match
                print("added siexact " + match)
                # try to match unit in units table
                unt = Units.objects.filter(name=match)
                if unt:
                    u = unt[0]
                    found.unit_id = u.id
                    print("added unit ID " + str(u.id))
            if not found.defunitsystems and hit.defu:
                # definedUnitOfSystem 298
                found.defunitsystems = hit.defu.replace('http://qudt.org/vocab/sou/', '')
                print("added defunitsystems " + hit.defu)
            if not found.dercohsystems and hit.defc:
                # derivedCoherentUnitOfSystem 127
                found.dercohsystems = hit.defc.replace('http://qudt.org/vocab/sou/', '')
                print("added dercohsystem " + hit.defc)
            if not found.derunitsystems and hit.defs:
                # derivedUnitOfSystem 99
                found.derunitsystems = hit.defs.replace('http://qudt.org/vocab/sou/', '')
                print("added derunitsystems " + hit.defs)
            if not found.multiplier and hit.mult:
                # conversionMultiplier
                found.multiplier = hit.mult
                print("added multiplier " + hit.mult)
            if not found.omunit and hit.uom2:
                # omUnit
                uo = hit.uom2.replace('http://www.ontology-of-units-of-measure.org/resource/om-2/', '')
                found.omunit = uo
                print("added omunit unit " + uo)
            if not found.ieccodes and hit.iecs:
                # iec61360Code
                iecs = list(set(hit.iecs.split(' ')))
                found.ieccodes = "'" + "', '".join(iecs) + "'"
                print("added iec codes " + found.ieccodes)
            if not found.ucumcodes and hit.ucums:
                # ucumCode
                ucs = list(set(hit.ucums.split(' ')))
                found.ucumcodes = "'" + "', '".join(ucs) + "'"
                print("added ucum codes " + found.ucumcodes)
            if not found.unececodes and hit.unecs:
                # uneceCommonCode
                uns = list(set(hit.unecs.split(' ')))
                found.unececodes = "'" + "', '".join(uns) + "'"
                print("added unece codes " + found.unececodes)
            if not found.symbol and hit.sym:
                # symbol
                found.symbol = hit.sym
                print("added symbol " + hit.sym)
            if not found.normrefs and hit.iso:
                # isoNormativeReference
                print("add code - normrefs")
                exit()
            if not found.infrefs and hit.infs:
                # informativeReference
                infs = list(set(hit.infs.split(' ')))
                found.infrefs = "'" + "', '".join(infs) + "'"
                print("added infrefs " + found.infrefs)
            if not found.description and hit.desc:
                # description
                desc = hit.desc.replace('$', '')
                found.description = LatexNodes2Text().latex_to_text(desc)
                print("added description")
            if not found.altlabel and hit.alt:
                # altLabel
                found.altlabel = hit.alt
                print("added altlabel " + hit.alt)
            if not found.dbpedia and hit.dbp:
                # dbpediaMatch
                found.dbpedia = hit.dbp
                print("added dbpedia " + hit.dbp)
            if not found.latexsymbol and hit.tex:
                # latexDefinition
                found.latexsymbol = hit.tex
                print("add latex defn " + hit.tex)
            found.save()
            print("unit " + hit.name + " updated")
        else:
            # add new unit
            newunit = Qudtunits(name=hit.name)
            newunit.code = hit.unit.replace('http://qudt.org/vocab/unit/', '')
            newunit.dimvector = hit.vec.replace('http://qudt.org/vocab/dimensionvector/', '')
            if hit.siex:
                newunit.siexact = hit.siex.replace('https://si-digital-framework.org/SI/units/', '')
                # check for unit table match
                unt = Units.objects.filter(name=newunit.siexact)
                if unt:
                    u = unt[0]
                    newunit.unit_id = u.id
            if hit.defu:
                newunit.defunitsystems = hit.defu
            if hit.defc:
                newunit.dercohsystems = hit.defc
            if hit.defs:
                newunit.derunitsystems = hit.defs
            if hit.mult:
                newunit.multiplier = hit.mult
            if hit.uom2:
                newunit.omunit = hit.uom2
            if hit.iecs:
                iecs = list(set(hit.iecs.split(' ')))
                newunit.ieccodes = "'" + "', '".join(iecs) + "'"
            if hit.ucums:
                ucs = list(set(hit.ucums.split(' ')))
                newunit.ucumcodes = "'" + "', '".join(ucs) + "'"
            if hit.unecs:
                uns = list(set(hit.unecs.split(' ')))
                newunit.unececodes = "'" + "', '".join(uns) + "'"
            if hit.sym:
                newunit.symbol = hit.sym
            if hit.iso:
                newunit.normrefs = hit.iso
            if hit.infs:
                infs = list(set(hit.infs.split(' ')))
                newunit.infrefs = "'" + "', '".join(infs) + "'"
            if hit.desc:
                newunit.description = LatexNodes2Text().latex_to_text(hit.desc)
            if hit.alt:
                newunit.altlabel = hit.alt
            if hit.dbp:
                newunit.dbpedia = hit.dbp
            if hit.tex:
                newunit.latexsymbol = hit.tex
            # save new unit
            newunit.updated = jax.localize(datetime.now())
            newunit.save()
            print(newunit.__dict__)
            # add the join table entries
            # unitsystems_qudtunits
            syss = list(set(hit.syss.split(' ')))  # not sure why there are duplicates sometimes
            ns = 'http://qudt.org/vocab/quantitykind/'
            abbs = (UnitsystemsQudtunits.objects.filter(qudtunit_id=newunit.id).
                    values_list('unitsystem__abbrev', flat=True))
            joinusqu(newunit, syss, usyss, 0, ns, abbs)
            # quantitysystems_qudtunits
            kinds = list(set(hit.kinds.split(' ')))  # not sure why there are duplicates sometimes
            codes = (QudtqkindsQudtunits.objects.filter(qudtunit_id=newunit.id).
                     values_list('qudtqkind__code', flat=True))
            ns = 'http://qudt.org/vocab/quantitykind/'
            joinqkqu(newunit, kinds, qkinds, 0, ns, codes)
            exit()


def ingestkinds():
    url = ('https://raw.githubusercontent.com/qudt/qudt-public-repo/main/vocab/quantitykinds/VOCAB_QUDT-QUANTITY-KINDS'
           '-ALL-v2.1.ttl')
    resp = requests.get(url)
    rdf = resp.text
    g = Graph()
    g.parse(rdf.encode("utf-8")).serialize(format="json-ld")
    qudtkind = """
    PREFIX qk: <http://qudt.org/vocab/quantitykind/>
    PREFIX qudt: <http://qudt.org/schema/qudt/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX qudt: <http://qudt.org/schema/qudt/>
    PREFIX qk: <http://qudt.org/vocab/quantitykind/>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX qkdv: <http://qudt.org/vocab/dimensionvector/>

    SELECT  ?name ?vec ?abbr ?cgsd ?impd ?isod ?siud ?uscd ?dep ?xact ?texd ?texs ?text ?siem ?sym ?cmmt ?brdr
            (group_concat(DISTINCT(?unt)) as ?unts)
            (IF(?nrm = Null ) as ?nrms)
            WHERE {
                ?kind   rdf:type qudt:QuantityKind;
                        rdfs:label ?name ;
                        qudt:applicableUnit|qudt:applicableSIUnit ?unt .
                OPTIONAL { ?kind qudt:abbreviation ?abbr . }
                OPTIONAL { ?kind qudt:baseCGSUnitDimensions ?cgsd . }
                OPTIONAL { ?kind qudt:baseImperialUnitDimensions ?impd . }
                OPTIONAL { ?kind qudt:baseISOUnitDimensions ?isod . }
                OPTIONAL { ?kind qudt:baseSIUnitDimensions ?siud . }
                OPTIONAL { ?kind qudt:baseUSCustomaryUnitDimensions ?uscd . }
                OPTIONAL { ?kind qudt:deprecated ?dep . }
                OPTIONAL { ?kind qudt:exactMatch ?xact . }
                OPTIONAL { ?kind qudt:hasDimensionVector ?vec . }
                OPTIONAL { ?kind qudt:latexDefinition ?texd . }
                OPTIONAL { ?kind qudt:latexSymbol ?texs . }
                OPTIONAL { ?kind qudt:normativeReference ?nrm . }
                OPTIONAL { ?kind qudt:plainTextDescription ?text . }
                OPTIONAL { ?kind qudt:qkdvDenominator ?dvec . }
                OPTIONAL { ?kind qudt:qkdvNumerator ?nvec . }
                OPTIONAL { ?kind qudt:siExactMatch ?siem . }
                OPTIONAL { ?kind qudt:symbol ?sym . }
                OPTIONAL { ?kind rdfs:seeAlso ?see . }
                OPTIONAL { ?kind rdfs:comment ?cmmt . }
                OPTIONAL { ?kind skos:broader ?brdr . }
                OPTIONAL { ?kind skos:closeMatch ?cls . }
                OPTIONAL { ?kind skos:altLabel ?alt . }
                FILTER(LANG(?name) = "en")
            }
            GROUP BY ?name ?vec ?abbr ?cgsd ?impd ?isod ?siud ?uscd ?dep ?xact ?texd ?texs ?text ?siem ?sym ?cmmt ?brdr
    """
    kinds = g.query(qudtkind)
    for hit in kinds:
        print(hit)
        exit()


def joinusqu(unit, syss, usyss, cnt, ns, abbs):
    for sys in syss:
        abb = sys.replace(ns, '')
        print(abbs)
        if abbs:
            if abb in abbs:  # skip if present
                continue
        cnt += 1
        usu = UnitsystemsQudtunits(unitsystem_id=usyss[abb], qudtunit_id=unit.id, updated=jax.localize(datetime.now()))
        usu.save()
        print('added unitsystem ' + abb)
    return


def joinqkqu(unit, kinds, qkinds, cnt, ns, codes):
    for kind in kinds:
        code = kind.replace(ns, '')
        if code in codes:  # skip if present
            continue
        cnt += 1
        qku = QudtqkindsQudtunits(qudtqkind_id=qkinds[code], qudtunit_id=unit.id, updated=jax.localize(datetime.now()))
        qku.save()
        print('added quantitykind ' + code)
    return


ingestkinds()
