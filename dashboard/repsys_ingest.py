"""
functions to access the repsystem data where it is published
this means one function per syste :(
"""
from units.models import *
from umisconfig.settings import *
from bs4 import BeautifulSoup
from qwikidata.sparql import return_sparql_query_results
from rdflib import Graph
import os
import requests
import json


def getrepsystemdata(rsid):
    repsys = Repsystems.objects.values('fileformat').get(id=rsid)
    ext = repsys['fileformat']
    with open(os.path.join(BASE_DIR, STATIC_URL, f'repsys_{rsid}{ext}'), 'r') as f:
        rsfile = f.read()
    data = ''
    if rsid == 15:
        data = getiecdata(rsfile)
    elif rsid == 7:
        data = getwikidata(rsfile)
    elif rsid == 10:
        data = getqudt(rsfile)
    else:
        print("write the code!")
        exit()
    with open(os.path.join(BASE_DIR, STATIC_URL, f'repsys_{rsid}_data.json'), 'w') as f:
        if rsid == 10:
            jsn = data
        else:
            jsn = json.dumps(data)
        f.write(jsn)
        f.close()
    repsysobj = Repsystems.objects.get(id=rsid)
    repsysobj.jsondata = jsn
    repsysobj.save()
    return data


def getiecdata(rsfile):
    data = BeautifulSoup(rsfile, "html.parser")
    units = data.select("a[href*=OpenDocument]")
    ulist = []
    for unit in units:
        ulist.append({'url': unit['href'], 'code': unit.contents[0]})

    """ get data from unit HTML page and add to ulist """
    for key, unit in enumerate(ulist):
        url = 'https://cdd.iec.ch' + unit['url']
        hpage = requests.get(url)
        upage = BeautifulSoup(hpage.content, "html.parser")
        tbl = upage.find(id="contentL1")
        data = {}
        for row in tbl.find_all('tr'):
            cells = row.find_all('td')
            name = cells[0].text.strip('\n :')
            value = cells[1].text.strip('\n ')
            data.update({name: value})
        unit.update({'name': data['Preferred name']})
        unit.update({'shortname': data['Short name']})
        unit.update({'definition': data['Definition']})
        unit.update({'unece': data['Remark'].replace('UN/ECE code: ', '')})
        quants = data['Applicable list of units'].replace('0112/', ',0112/').strip(",").split(",")
        unit.update({'quantities': quants})
        ulist[key] = unit
    return ulist


def getwikidata(rsfile):
    data = return_sparql_query_results(rsfile)
    # add to the entities table
    for hit in data['results']['bindings']:
        if "http://www.wikidata.org/entity/Q" not in hit['unit']['value']:
            # russian entries
            continue
        wdid = hit['unit']['value'].replace("http://www.wikidata.org/entity/", "")
        if wdid == hit['unitLabel']['value']:
            # entries where name is not defined
            continue
        print(wdid)
        print(hit)
        exit()
    return data


def getqudt(rsfile):
    tmp = rsfile.encode("utf-8")  # required to process correctly
    g = Graph()
    g.parse(tmp)
    jld = g.serialize(format="json-ld")
    return jld
