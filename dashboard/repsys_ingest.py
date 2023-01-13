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
from datetime import datetime
import os
import requests
import json
import yaml
import pytz
import re


def getrepsystemdata(rsid):
    """ function to get data (as a ...data.json file) for a repsys if it's been generated or not """
    repsys = Repsystems.objects.values('fileformat', 'url').get(id=rsid)
    ext = repsys['fileformat']
    data = []
    jsn = ''
    if not os.path.exists(os.path.join(BASE_DIR, STATIC_URL, f'repsys_{rsid}_data.json')):
        # get and send the raw data file for repsys to function to create json data file
        if ext == 'url':
            rsfile = requests.get(repsys['url'])
        else:
            rawpath = os.path.join(BASE_DIR, STATIC_URL, f'repsys_{rsid}{ext}')
            if not os.path.exists(rawpath):
                print('raw file is not present')
                exit()
            with open(rawpath, 'r') as f:
                rsfile = f.read()

        if rsid == 3:
            data = getgbdata(rsfile)
        elif rsid == 5:
            # raw file is ready to import directly
            # this does not get used as the data file always exists...
            pass
        elif rsid == 6:
            # raw file is ready to import directly
            # this does not get used as the data file always exists...
            pass
        elif rsid == 7:
            data = getwikidata(rsfile)
        elif rsid == 8:
            data = getuo(rsfile)
        elif rsid == 9:
            data = getncit(rsfile)
        elif rsid == 10:
            data = getqudt(rsfile)
        elif rsid == 15:
            data = getiecdata(rsfile)
        elif rsid == 16:
            # raw file is ready to import directly
            # this does not get used as the data file always exists...
            pass
        elif rsid == 19:
            data = getunitsml(rsfile)
        else:
            print("write the code!")
            exit()
        # convert to json and save
        if jsn == '':  # checks if jsn has already been populated above...
            jsn = json.dumps(data)
            with open(os.path.join(BASE_DIR, STATIC_URL, f'repsys_{rsid}_data.json'), 'w') as f:
                f.write(jsn)
                f.close()
    else:
        # get the json data
        with open(os.path.join(BASE_DIR, STATIC_URL, f'repsys_{rsid}_data.json'), 'r') as f:
            jsn = f.read()
            f.close()
            data = json.loads(jsn)

    # update repsystems table with current data
    repsysobj = Repsystems.objects.get(id=rsid)
    repsysobj.jsondata = jsn
    repsysobj.save()
    return data


def getgbdata(rsfile):
    e = json.loads(rsfile)
    entries = e['entries']
    units = []
    for entry in entries:
        if entry['index'] == 'unit':
            u = {}
            u.update({'name': entry['term']})
            u.update({'code': entry['code']})
            if isinstance(entry['definition'], list):
                u.update({'defn': entry['definition'][0]})
            else:
                u.update({'defn': entry['definition']})
            units.append(u)
    return units


def getiecdata(rsfile):
    # get the data in the IEC CDD and save it as files for quantities and units
    rsid = 15
    repsysobj = Repsystems.objects.get(id=rsid)
    repsys = Repsystems.objects.values('id', 'url', 'fileupdated').get(id=rsid)
    # starting with the list of units page go out to all the quantities and record the units they point too
    # rsfile here is the HTML content from the URL in the DB 'url' field
    data = BeautifulSoup(rsfile.content, "html.parser")
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
    with open(os.path.join(BASE_DIR, STATIC_URL, f'repsys_{rsid}_data.json'), 'w') as f:
        f.write(juout)
        f.close()
    # update the DB record
    rdate = datetime.strptime(rsfile.headers['Last-Modified'], '%a, %d %b %Y %H:%M:%S %Z').date()
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
    return uout


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
    return json.loads(jld)


def getuo(rsfile):
    tmp = rsfile.encode("utf-8")  # required to process correctly
    g = Graph()
    g.parse(tmp, format='xml')
    jld = g.serialize(format="json-ld")
    return jld


ncitiris = []


def getncitunits(page):
    # recursive function to drill down levels in the NCIT ontology
    # required by the getncit function
    for term in page['_embedded']['terms']:
        if term['has_children']:
            clink = term['_links']['children']['href']
            newpage = requests.get(clink)
            jpage = json.loads(newpage.content)
            getncitunits(jpage)
        else:
            ncitiris.append(term['iri'])
    return ncitiris


def getncit(rsfile):
    # the starting data file as a json output of the OLS service
    # https://www.ebi.ac.uk/ols/api/ontologies/ncit/terms/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252FNCIT_C25709
    # variable to contain ncit units
    # generate new iris file

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


def getunitsml(rsfile):
    # data is in a yaml file from the GitHub repo (https://github.com/unitsml/unitsdb/blob/main/units.yaml)
    # file needs to be edited to add --- (indicator of different docs) so it can be processed below
    out = []
    units = yaml.safe_load_all(rsfile)
    for unit in units:
        keys = list(unit.keys())  # only one
        data = unit[keys[0]]
        u = {}
        u.update({'name': data['short']})
        u.update({'code': keys[0]})
        u.update({'type': data['unit_system']['type']})
        u.update({'symbol': data['unit_symbols'][0]['id']})
        u.update({'dimid': data['dimension_url']})
        quants = []
        quantids = []
        for quant in data['quantity_reference']:
            quants.append(quant['name'])
            quantids.append(quant['url'].replace('#', ''))
        u.update({'quantity': ', '.join(quants)})
        u.update({'quantityids': ', '.join(quantids)})
        out.append(u)
    return out
