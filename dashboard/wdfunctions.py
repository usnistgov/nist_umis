""" wikidata query functions"""
from qwikidata.sparql import return_sparql_query_results
import json


def wdclasses():
    """ get list of unit of measurement subclasses starting with 'unit of'"""
    query = """
    SELECT ?c ?class ?isq ?s ?src ?sect ?quant WHERE {
        ?c wdt:P279+ wd:Q47574 ;
            rdfs:label ?class .
        OPTIONAL { ?c wdt:P4020 ?isq . }
        OPTIONAL { ?c wdt:P1343 ?s . ?s rdfs:label ?src . }
        OPTIONAL { ?c wdt:P111 ?q . ?q rdfs:label ?quant . }
        OPTIONAL {
            ?c  p:P1343 ?r .  # ?r is the the statement node (triple)
            ?r  pq:P958 ?sect .  # this is an attribute (a qualifier) 
        }
        FILTER(LANG(?class) = "en")
        FILTER(LANG(?src) = "en")
        FILTER(LANG(?quant) = "en")
        FILTER(STRSTARTS(?class, "unit ")) 
        FILTER(CONTAINS(?src, "80000"))
    }
    """
    # search wikidata sparql query
    wd = return_sparql_query_results(query)
    # return data
    wdjsn = json.loads(json.dumps(wd['results']['bindings']))
    return wdjsn


def wdunits():
    """ get list of units of measurement instances under 'unit of' subclasses """
    query = """
    SELECT ?curl ?cls ?uurl ?unit ?qurl ?quant ?factor ?facunit ?iev ?igb ?ncit ?qudt ?ucum ?unece ?uom2 ?wolf ?wur WHERE  { 
      ?curl wdt:P279* wd:Q47574 ;
             rdfs:label ?cls .
      ?uurl wdt:P31 ?curl ;
            rdfs:label ?unit .
      OPTIONAL { ?uurl wdt:P111 ?qurl . ?qurl rdfs:label ?quant . }
      OPTIONAL {
        ?uurl p:P2370 ?node .
        ?node psv:P2370 ?f .
        ?f wikibase:quantityAmount ?fstr .
        ?f wikibase:quantityUnit ?facunit .
        BIND(SUBSTR(?fstr, 1, 50) as ?factor)
      }
      OPTIONAL { ?uurl wdt:P1748 ?ncit }
      OPTIONAL { ?uurl wdt:P2892 ?umls }
      OPTIONAL { ?uurl wdt:P2968 ?qudt }
      OPTIONAL { ?uurl wdt:P3328 ?wur }
      OPTIONAL { ?uurl wdt:P4732 ?igb }
      OPTIONAL { ?uurl wdt:P6512 ?unece }
      OPTIONAL { ?uurl wdt:P7007 ?wolf }
      OPTIONAL { ?uurl wdt:P7825 ?ucum }
      OPTIONAL { ?uurl wdt:P8769 ?uom2 }
      OPTIONAL { ?uurl wdt:P8855 ?iev }
      FILTER(?qurl NOT IN (wd:Q8142, wd:Q82047057, wd:Q83155724, 
        wd:Q1499468, wd:Q11639620, wd:Q28783456, wd:Q3622170, wd:Q28805608))
      FILTER(STRSTARTS(?cls, "unit of ")) 
      FILTER(!REGEX(?unit, "Q[0-9]+", "i"))
      FILTER(LANG(?cls) = "en")
      FILTER(LANG(?unit) = "en")
      FILTER(LANG(?quant) = "en")
    }
    ORDER BY ?quant
    """
    # search wikidata sparql query
    wd = return_sparql_query_results(query)
    # return data
    wdjsn = json.loads(json.dumps(wd['results']['bindings']))
    return wdjsn


def wdquants():
    """ get list of units of measurement instances under 'unit of' subclasses """
    # filtering based on ISO sources (incomplete) for example (currently limits responses severely)
    # FILTER(?srcid IN(wd:Q109490582,wd:Q90137277,wd:Q73391977,wd:Q92157468,wd:Q117847945,
    # wd:Q80232369,wd:Q99839315,wd:Q86976044,wd:Q85490171,wd:Q100957475))
    query = """
    SELECT DISTINCT ?qntid ?quant ?isq ?source ?sect
    WHERE
    {
        ?untid wdt:P111 ?qntid .
        ?qntid rdfs:label ?quant .
        OPTIONAL {?qntid wdt:P4020 ?isq }
        OPTIONAL { 
            ?qntid wdt:P1343 ?srcid .
            ?srcid rdfs:label ?source .
            FILTER(CONTAINS(?source, ":2019")||CONTAINS(?source, ":2020")||CONTAINS(?source, ":2022"))
            FILTER(LANG(?source) = "en") .
        }
        OPTIONAL {
            ?qntid wdt:P8111 ?untid .
            ?untid rdfs:label ?unit .
            FILTER(LANG(?unit) = "en") .
        }
        OPTIONAL {
            ?qntid p:P1343 ?qual .
            ?qual pq:P958 ?sect .  # this is an attribute (a qualifier) 
        }
        FILTER(LANG(?quant) = "en") .
    }
    ORDER BY ASC(?quant)
    """
    # search wikidata sparql query
    wd = return_sparql_query_results(query)
    # return data
    wdjsn = json.loads(json.dumps(wd['results']['bindings']))
    return wdjsn


def wdsiclss():
    """ get list of unit of measurement subclasses starting with 'unit of'"""
    query = """
    SELECT ?curl ?cls ?uurl ?unit WHERE  { 
      ?curl wdt:P279* wd:Q47574 ;
             rdfs:label ?cls .
      ?uurl wdt:P31 ?curl ;
            rdfs:label ?unit .
      FILTER(?curl IN (wd:Q223662, wd:Q208469, wd:Q61610698, wd:Q87252761, wd:Q68618328, wd:Q1618549, wd:Q21684377,
                       wd:Q69197847, wd:Q99734981, wd:Q26240, wd:Q106839753, wd:Q3268848, wd:Q106839917))
      FILTER(LANG(?cls) = "en")
      FILTER(LANG(?unit) = "en")
    }
    ORDER BY ?cls
    """
    # search wikidata sparql query
    wd = return_sparql_query_results(query)
    # return data
    wdjsn = json.loads(json.dumps(wd['results']['bindings']))
    return wdjsn


def wdunit(wdid):
    query = """
    SELECT DISTINCT ?unit ?factor ?facunit ?iev ?igb ?ncit ?qudt ?ucum ?unece ?uom2 ?wolf ?wur WHERE  { 
      ?wdid wdt:P31 ?curl ;
            rdfs:label ?unit .
      OPTIONAL {
        ?wdid p:P2370 ?node .
        ?node psv:P2370 ?f .
        ?f wikibase:quantityAmount ?factor .
        ?f wikibase:quantityUnit ?facunit .
      }
      OPTIONAL { ?wdid wdt:P1748 ?ncit }
      OPTIONAL { ?wdid wdt:P2892 ?umls }
      OPTIONAL { ?wdid wdt:P2968 ?qudt }
      OPTIONAL { ?wdid wdt:P3328 ?wur }
      OPTIONAL { ?wdid wdt:P4732 ?igb }
      OPTIONAL { ?wdid wdt:P6512 ?unece }
      OPTIONAL { ?wdid wdt:P7007 ?wolf }
      OPTIONAL { ?wdid wdt:P7825 ?ucum }
      OPTIONAL { ?wdid wdt:P8769 ?uom2 }
      OPTIONAL { ?wdid wdt:P8855 ?iev }
      FILTER(LANG(?unit) = "en")
    }
    """
    query = query.replace("?wdid", "wd:" + wdid)
    # search wikidata sparql query
    wd = return_sparql_query_results(query)
    # return data
    wdjsn = json.loads(json.dumps(wd['results']['bindings']))
    return wdjsn
