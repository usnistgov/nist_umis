"""
functions to access the repsystem data where it is published
this means one function per system :(
"""
from units.models import *
from umisconfig.settings import *
from bs4 import BeautifulSoup
from datetime import date
from qwikidata.sparql import return_sparql_query_results
from rdflib import Graph
from urllib import parse
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
    elif rsid == 8:
        data = getuo(rsfile)
    elif rsid == 9:
        data = getncit(rsfile)
    elif rsid == 10:
        data = getqudt(rsfile)
    else:
        print("write the code!")
        exit()
    with open(os.path.join(BASE_DIR, STATIC_URL, f'repsys_{rsid}_data.json'), 'w') as f:
        if rsid == 8 or rsid == 10:
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
    rsid = 7
    # check if the data file has been updated today or not
    path = os.path.join(BASE_DIR, STATIC_URL, f'repsys_{rsid}_data.json')
    ts = os.path.getmtime(path)
    udate = date.fromtimestamp(ts)
    today = date.today()
    if udate < today:
        # get data
        data = return_sparql_query_results(rsfile)
        # update file
        jdata = json.dumps(data)
        with open(os.path.join(BASE_DIR, STATIC_URL, f'repsys_{rsid}_data.json'), 'w') as f:
            f.write(jdata)
            f.close()
        print("updated")
    else:
        print("no update")
        with open(os.path.join(BASE_DIR, STATIC_URL, f'repsys_{rsid}_data.json'), 'r') as f:
            jdata = f.read()
            f.close()
        data = json.loads(jdata)
    return data


def getqudt(rsfile):
    tmp = rsfile.encode("utf-8")  # required to process correctly
    g = Graph()
    g.parse(tmp)
    jld = g.serialize(format="json-ld")
    return jld


def getuo(rsfile):
    tmp = rsfile.encode("utf-8")  # required to process correctly
    g = Graph()
    g.parse(tmp, format='xml')
    jld = g.serialize(format="json-ld")
    return jld


def getncitunits(page):
    for term in page['_embedded']['terms']:
        if term['has_children']:
            clink = term['_links']['children']['href']
            newpage = requests.get(clink)
            jpage = json.loads(newpage.content)
            getncitunits(jpage)
        else:
            ncitiris.append(term['iri'])
    return True


ncitiris = []


def getncit(rsfile):
    # the starting data file as a json output of the OLS service
    # https://www.ebi.ac.uk/ols/api/ontologies/ncit/terms/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252FNCIT_C25709
    # variable to contain ncit units
    out, iris = [], []
    if not os.path.exists(os.path.join(BASE_DIR, STATIC_URL, f'repsys_9_data.json')):
        if os.path.exists(os.path.join(BASE_DIR, STATIC_URL, f'repsys_9_iris.json')):
            # read in the file
            with open(os.path.join(BASE_DIR, STATIC_URL, f'repsys_9_iris.json'), 'r') as f:
                tmp = f.read()
                iris = json.loads(tmp)
                f.close()
        else:
            data = json.loads(rsfile)
            if data['has_children']:
                clink = data['_links']['children']['href']
                newpage = requests.get(clink)
                jpage = json.loads(newpage.content)
                getncitunits(jpage)
            iris = ncitiris
            # write out the file
            with open(os.path.join(BASE_DIR, STATIC_URL, f'repsys_9_iris.json'), 'w') as f:
                jsn = json.dumps(iris)
                f.write(jsn)
                f.close()
        # get unit data
        for unit in iris:
            # url requires encoding "/" using safe='' in parse.quote and then 'double' encoding the '%' as '%25'
            termpath = 'https://www.ebi.ac.uk/ols/api/ontologies/ncit/terms/'
            uurl = termpath + parse.quote(unit, safe='').replace('%', '%25')
            upage = requests.get(uurl)
            udata = json.loads(upage.content)
            if udata['is_obsolete']:
                continue
            print(udata['iri'])
            u = {}
            u.update({'name': udata['annotation']['Preferred_Name'][0]})
            desc = None
            if len(udata['description']) > 0:
                desc = udata['description'][0]
            u.update({'description': desc})
            u.update({'value': udata['annotation']['code'][0]})
            symbol = None
            for syn in udata['synonyms']:
                if not symbol:
                    symbol = syn
                elif len(syn) < len(symbol):
                    symbol = syn
            u.update({'symbol': symbol})
            # get quantity
            qurl = udata['_links']['hierarchicalParents']['href']
            qpage = requests.get(qurl)
            qdata = json.loads(qpage.content)
            qdata = qdata['_embedded']['terms'][0]
            quant = qdata['annotation']['Preferred_Name'][0].replace('Unit of ', '').lower()
            u.update({'quantity': quant})
            out.append(u)
        # save file
        with open(os.path.join(BASE_DIR, STATIC_URL, f'repsys_9_data.json'), 'w') as f:
            jsn = json.dumps(out)
            f.write(jsn)
            f.close()
    else:
        # read file
        with open(os.path.join(BASE_DIR, STATIC_URL, f'repsys_9_data.json'), 'r') as f:
            out = f.read()
            f.close()
    return out
