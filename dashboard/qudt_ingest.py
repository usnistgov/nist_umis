"""ingest of units and quantities from wikidata"""
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
                nrms = list(set(hit.iso.split(' ')))
                found.normrefs = "'" + "', '".join(nrms) + "'"
                print("add code - normrefs")
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
            if hit.syss:
                print('unit systems: ' + hit.syss)
                syss = list(set(hit.syss.split(' ')))  # not sure why there are duplicates sometimes
                ns = 'http://qudt.org/vocab/sou/'
                joinusqu(newunit, syss, usyss, 0, ns, [])
            # quantitysystems_qudtunits
            if hit.kinds != '':
                kinds = list(set(hit.kinds.split(' ')))  # not sure why there are duplicates sometimes
                ns = 'http://qudt.org/vocab/quantitykind/'
                joinqkqu(newunit, kinds, qkinds, 0, ns, [])
            # exit()


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

    SELECT  ?qkind ?kind ?vec ?abbr ?cgsd ?impd ?isod ?siud ?uscd ?dep ?desc ?xact ?texd
            ?texs ?iref ?iso ?nrm ?text ?dvec ?nvec ?siem ?sym ?see ?cmmt ?brdr ?cls ?alt
            (group_concat(DISTINCT(?unit)) as ?units)
            WHERE {
                ?qkind  rdf:type qudt:QuantityKind;
                        rdfs:label ?kind ;
                        qudt:applicableUnit|qudt:applicableSIUnit ?unit .
                OPTIONAL { ?qkind qudt:abbreviation ?abbr . }
                OPTIONAL { ?qkind qudt:baseCGSUnitDimensions ?cgsd . }
                OPTIONAL { ?qkind qudt:baseImperialUnitDimensions ?impd . }
                OPTIONAL { ?qkind qudt:baseISOUnitDimensions ?isod . }
                OPTIONAL { ?qkind qudt:baseSIUnitDimensions ?siud . }
                OPTIONAL { ?qkind qudt:baseUSCustomaryUnitDimensions ?uscd . }
                OPTIONAL { ?qkind qudt:deprecated ?dep . }
                OPTIONAL { ?qkind dcterms:description ?desc . }
                OPTIONAL { ?qkind qudt:hasDimensionVector ?vec . }
                OPTIONAL { ?qkind qudt:latexDefinition ?texd . }
                OPTIONAL { ?qkind qudt:latexSymbol ?texs . }
                OPTIONAL { ?qkind qudt:informativeReference ?iref . }
                OPTIONAL { ?qkind qudt:isoNormativeReference ?iso . }
                OPTIONAL { ?qkind qudt:normativeReference ?nrm . }
                OPTIONAL { ?qkind qudt:plainTextDescription ?text . }
                OPTIONAL { ?qkind qudt:qkdvDenominator ?dvec . }
                OPTIONAL { ?qkind qudt:qkdvNumerator ?nvec . }
                OPTIONAL { ?qkind qudt:siExactMatch ?siem . }
                OPTIONAL { ?qkind qudt:symbol ?sym . }
                OPTIONAL { ?qkind rdfs:seeAlso ?see . }
                OPTIONAL { ?qkind rdfs:comment ?cmmt . }
                OPTIONAL { ?qkind skos:broader ?brdr . }
                OPTIONAL { ?qkind qudt:exactMatch ?xact . }
                OPTIONAL { ?qkind skos:closeMatch ?cls . }
                OPTIONAL { ?qkind skos:altLabel ?alt . FILTER(LANG(?alt) = "en") }
                FILTER(LANG(?kind) = "en")
            }
            GROUP BY ?qkind ?kind ?vec ?abbr ?cgsd ?impd ?isod ?siud ?uscd ?dep ?desc ?xact ?texd
                    ?texs ?iref ?iso ?nrm ?text ?dvec ?nvec ?siem ?sym ?see ?cmmt ?brdr ?cls ?alt
            ORDER BY ?kind
    """
    kinds = g.query(qudtkind)
    # print(len(kinds))
    # exit()
    for hit in kinds:
        code = hit.qkind.replace('http://qudt.org/vocab/quantitykind/', '')
        print("**starting " + code + "**")
        foundall = Qudtqkinds.objects.filter(code=code)
        if foundall:
            found = foundall[0]
            if found.name:
                print("quantity kind " + found.name + " already updated")
                continue
            if not found.name and hit.qkind:
                # name
                found.name = hit.kind
                print("added name " + found.name)
            if not found.dimvector and hit.vec:
                # hasDimensionVector
                found.dimvector = hit.vec.replace('http://qudt.org/vocab/dimensionvector/', '')
                print("added dimension vector " + found.dimvector)
            if not found.deprecated and hit.dep:
                # deprecated
                found.deprecated = hit.dep
                print("added deprecated " + found.deprecated)
            if not found.units and hit.units:
                # QUDT codes as a comma delimited list
                units = list(set(hit.units.split(' ')))  # not sure why there are duplicates sometimes
                uarr = []
                for unit in units:
                    uarr.append(unit.replace('http://qudt.org/vocab/unit/', ''))
                found.units = ",".join(uarr)
                print("added units " + found.units)
            if not found.description and hit.desc:
                # latex based description
                found.description = hit.desc.replace('http://purl.org/dc/terms/', '')
                print("added description")
            if not found.text and hit.text:
                # plain text description
                found.text = hit.text
                print("added plain text description")
            if not found.ddimvector and hit.dvec:
                # denominator dimension vector
                found.ddimvector = hit.dvec.replace('http://qudt.org/vocab/dimensionvector/', '')
                print("added denominator dimension vector " + found.ddimvector)
            if not found.ndimvector and hit.nvec:
                # numerator dimension vector
                found.ndimvector = hit.nvec.replace('http://qudt.org/vocab/dimensionvector/', '')
                print("added numerator dimension vector " + found.ddimvector)
            if not found.basecgsdims and hit.cgsd:
                # CGS dimensions
                found.basecgsdims = hit.cgsd.replace('$', '')
                print("added CGS dimensions " + found.basecgsdims)
            if not found.baseimpdims and hit.impd:
                # Imperial dimensions
                found.baseimpdims = hit.impd.replace('$', '')
                print("added Imperial dimensions " + found.baseimpdims)
            if not found.baseisodims and hit.isod:
                # ISO dimensions
                found.baseisodims = hit.isod.replace('$', '')
                print("added ISO dimensions " + found.baseisodims)
            if not found.basesidims and hit.siud:
                # SI dimensions
                found.basesidims = hit.siud.replace('$', '')
                print("added SI dimensions " + found.basesidims)
            if not found.altlabels and hit.alt:
                # plain text description
                found.altlabels = hit.alt
                print("added alt label " + found.altlabels)
            if not found.nrefs and hit.nrm:
                # normative reference
                found.nrefs = hit.nrm
                print("added normative ref " + found.nrefs)
            if not found.infrefs and hit.iref:
                # informative reference
                found.infrefs = hit.iref
                print("added informative ref " + found.infrefs)
            if not found.isorefs and hit.iso:
                # ISO reference
                found.isorefs = hit.iso
                print("added ISO ref " + found.isorefs)
            if not found.latexdefn and hit.texd:
                # latex definition
                found.latexdefn = hit.texd
                print("added LaTeX definition " + found.latexdefn)
            if not found.latexsymb and hit.texs:
                # latex symbol
                found.latexsymb = hit.texs
                print("added LaTeX symbol " + found.latexsymb)
            if not found.symbols and hit.sym:
                # latex symbol
                found.symbols = hit.sym
                print("added symbol(s) " + found.symbols)
            if not found.matches and hit.siem:
                # SI exact match
                found.matches = hit.siem.replace('https://si-digital-framework.org/SI/quantities/', '')
                print("added SI exact match " + found.matches)
            if not found.cmatches and hit.cls:
                # SKOS close match
                found.cmatches = hit.cls.replace('http://qudt.org/vocab/quantitykind/', '')
                print("added SKOS close match " + found.cmatches)
            if not found.ematches and hit.xact:
                # SKOS exact match
                found.ematches = hit.xact.replace('http://www.w3.org/2004/02/skos/core#', '')
                print("added SKOS exact match " + found.ematches)
            if not found.broader and hit.brdr:
                # SKOS broader
                found.broader = hit.brdr.replace('http://www.w3.org/2004/02/skos/core#', '')
                print("added SKOS broader " + found.broader)
            if not found.seealso and hit.see:
                # RDFS see also
                found.seealso = hit.see.replace('http://www.w3.org/2000/01/rdf-schema#', '')
                print("added RDFS see also " + found.seealso)
            if not found.abbrevs and hit.abbr:
                # abbreviation
                found.abbrevs = hit.abbr.replace('http://www.w3.org/2000/01/rdf-schema#', '')
                print("added abbreviation " + found.abbrevs)
            if not found.comments and hit.cmmt:
                # comment
                found.comments = hit.cmmt
                print("added comment " + found.comments)
            found.save()
            print("updated unit " + found.name)
        else:
            # add new unit
            newkind = Qudtqkinds(name=hit.kind)
            newkind.code = hit.qkind.replace('http://qudt.org/vocab/quantitykind/', '')
            units = hit.units.split(" ")
            uarr = []
            for unit in units:
                uarr.append(unit.replace('http://qudt.org/vocab/unit/', ''))
            newkind.units = " ".join(uarr)
            newkind.dimvector = hit.vec.replace('http://qudt.org/vocab/dimensionvector/', '')
            if hit.dep:
                newkind.deprecated = 'yes'
            else:
                newkind.deprecated = 'no'
            if hit.desc:
                temp = hit.desc.replace('\n', '').replace('  ', ' ').strip()
                newkind.description = temp.replace('  ', ' ')
            if hit.text:
                temp = hit.text.replace('\n', '').replace('  ', ' ').strip()
                newkind.text = temp.replace('  ', ' ')
            if hit.dvec:
                newkind.ddimvector = hit.dvec
            if hit.nvec:
                newkind.ndimvector = hit.nvec
            if hit.cgsd:
                newkind.basecgsdims = hit.cgsd
            if hit.impd:
                newkind.baseimpdims = hit.impd
            if hit.isod:
                newkind.baseisodims = hit.isod
            if hit.siud:
                newkind.basesidims = hit.siud
            if hit.alt:
                newkind.altlabels = hit.alt
            if hit.nrm:
                newkind.nrefs = hit.nrm
            if hit.iref:
                newkind.infrefs = hit.iref
            if hit.nrm:
                newkind.isorefs = hit.iso
            if hit.texd:
                newkind.latexdefn = hit.texd
            if hit.texs:
                newkind.latexsymb = hit.texs
            if hit.sym:
                newkind.symbols = hit.sym
            if hit.siem:
                newkind.matches = hit.siem.replace('https://si-digital-framework.org/SI/quantities/', '')
            if hit.cls:
                newkind.cmatches = hit.cls.replace('http://qudt.org/vocab/quantitykind/', '')
            if hit.xact:
                newkind.ematches = hit.xact.replace('http://www.w3.org/2004/02/skos/core#', '')
            if hit.brdr:
                newkind.broader = hit.brdr.replace('http://www.w3.org/2004/02/skos/core#', '')
            if hit.see:
                newkind.seealso = hit.see.replace('http://qudt.org/vocab/quantitykind/', '')
            if hit.abbr:
                newkind.abbrevs = hit.abbr.replace('http://www.w3.org/2000/01/rdf-schema#', '')
            if hit.cmmt:
                newkind.comments = hit.cmmt
            newkind.updated = jax.localize(datetime.now())
            # save new quantitykind
            newkind.save()
            print("add new quantity code " + newkind.code)
            # exit()


def joinusqu(unit, syss, usyss, cnt, ns, abbs):
    for sys in syss:
        abbr = sys.replace(ns, '')
        if abbs:
            if abbr in abbs:  # skip if present
                continue
        cnt += 1
        usu = UnitsystemsQudtunits(unitsystem_id=usyss[abbr], qudtunit_id=unit.id, updated=jax.localize(datetime.now()))
        usu.save()
        print('added unitsystem ' + abbr)
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


ingestunits()
