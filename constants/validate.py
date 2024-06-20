""" example code for the datafiles app"""
import os
import django
import math
import requests
import re

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "umisconfig.settings")
django.setup()

from constants.models import *
from bs4 import BeautifulSoup

run = "getreluncert"


if run == "idsval":
    """ consistency check on names and constant ids for values"""
    vals = Constantvalues.objects.all().values('id', 'constant_id', 'orig_name').order_by('constant_id')
    for val in vals:
        hits = Constants.objects.filter(allnames__contains="'" + val['orig_name'] + "'")
        print("checking '" + val['orig_name'] + "'")
        if hits.count() == 1:
            data = hits.values('id', 'allnames')[0]
            if data['id'] != val['constant_id']:
                print("constant id inconsistent!")
                print(val)
                print(data)
                exit()
        elif hits.count() > 1:
            print("multiple hits!")
            print(hits.values('id', 'allnames'))
            exit()
        else:
            print("not found!")
            print(val)
            exit()

if run == "numeric":
    """ check that the string and numeric values of the constants and uncertainties all match up """
    """ result: 625 values in sci. notation where off by 10^-14% in each case, others exact """
    vals = Constantvalues.objects.all().\
        values('id', 'orig_value', 'value_str', 'value_num', 'value_man', 'value_exp').order_by('constant_id')
    for val in vals:
        # print("checking " + val['orig_value'])
        val['orig_value'] = val['orig_value'].replace("…", "")
        oval = float(val['orig_value'].replace(" ", ""))
        sval = float(val['value_str'])
        nval = float(val['value_num'])
        xval = float(val['value_man'])*math.pow(10, val['value_exp'])
        if oval != sval:
            print("difference in sval for value " + str(val['id']))
            print(oval)
            print(sval)
        if oval != nval:
            print("difference in nval for value " + str(val['id']))
            print(oval)
            print(nval)
        if oval != xval:
            print("difference in xval for value " + str(val['id']))
            percent = (oval - xval)*100/oval
            print(str(percent) + "%")

if run == "scrape":
    """ scrape the NIST constants website links, page titles, and symbols (latex) """
    """ results: scraped 354 entries, ignored one failed link, missing pages for 14 constants """
    path = "https://physics.nist.gov"
    url = path + "/cgi-bin/cuu/Category?view=html&All+values.x=0"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    cnt = 0
    for link in soup.find_all('a'):
        if link.get('href').find('/cuu/Value') == -1:
            continue  # not found
        else:
            tmp = link.get('href').split('|')
            href = path + tmp[0]
            if href == 'https://physics.nist.gov/cgi-bin/cuu/Value?am':
                continue  # invalid page
            title = link.string.strip()
            # find constant in DB
            found = Constants.objects.filter(allnames__contains='"' + title + '"')
            hit = None
            if found.count() == 1:
                # save page to DB entry
                hit = found[0]
                if hit.nistpage is not None:
                    continue  # assume that entry has been updated if the page is not empty
                print("DB entry found for '" + title + "'")
                hit.nistpage = href
                hit.pagetitle = title
            elif found.count() > 1:
                print("multiple hits!")
                print(found.values('id', 'name'))
                exit()
            else:
                print("not found!")
                print(title)
                exit()
            # go to the page and get the symbol
            page = requests.get(href)
            const = BeautifulSoup(page.content, "html.parser")
            symbol = const.select("img[src*=Value]")
            hit.symbol = symbol[0]['alt']
            hit.save()
            print("DB entry '" + title + "' updated")
            if cnt > 99:
                exit()
            cnt = cnt + 1

if run == "calcrel":
    """ 
    calculate the relative uncertainty of the constants
    result: 101 2018 values had 'rel. uncert. mismatch' errors, presumably because of truncation of values/uncerts
    """
    vals = Constantvalues.objects.filter(orig_uncert__isnull=False, reluncert_man__isnull=True).\
        values('id', 'orig_name', 'constant_id', 'value_num', 'uncert_num', 'year')
    for val in vals:
        rel = float(val['uncert_num'])/float(val['value_num'])
        relstr = '{:.1E}'.format(rel)
        parts = relstr.split('E')
        man = parts[0]
        exp = parts[1]
        cmt = None
        # check consistency of rel. uncertainty values for 2018
        if int(val['year']) == 2018:
            # get url of page, the get content and check that the relative uncertainty matches what is calculated
            con = Constants.objects.get(id=val['constant_id'])
            page = requests.get(con.nistpage)
            const = BeautifulSoup(page.content, "html.parser")
            rows = const.findAll(size="4")
            text = rows[2].text.replace("\xa0", " ")  # replaces non-breaking space
            text = text.replace(" x 10", "E").strip(" ")
            if float(relstr) != float(text):
                print("mismatch")
                print(val['orig_name'])
                parts = text.split('E')
                man = parts[0]
                exp = parts[1]
                cmt = "rel. uncert. mismatch"
        # update the database entry
        upd = Constantvalues.objects.get(id=val['id'])
        upd.reluncert_man = man
        upd.reluncert_exp = exp
        upd.comments = cmt
        upd.save()
        print("Constant '" + val['orig_name'] + ":" + str(val['year']) + "'")

if run == 'getreluncert':
    path = "https://physics.nist.gov"
    url = path + "/cgi-bin/cuu/Category?view=html&All+values.x=0"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    cnt = 0
    year = '2022'
    for link in soup.find_all('a'):
        if link.get('href').find('/cuu/Value') == -1:
            continue  # not found
        else:
            tmp = link.get('href').split('|')
            href = path + tmp[0]
            if href == 'https://physics.nist.gov/cgi-bin/cuu/Value?am':
                continue  # invalid page
            title = link.string.strip()
            found = Constants.objects.filter(allnames__contains='"' + title + '"')
            if found.count() == 1:
                con = found[0]
                # get constant value for constant and year
                conid = con.id
                val = Constantvalues.objects.get(constant_id=conid, year=year)
                if val.reluncert_man is not None:
                    print(con.name + ' already added')
                    continue
                # go to the page and get the relative uncertainty
                page = requests.get(href)
                const = BeautifulSoup(page.content, "html.parser")
                rows = const.findAll("td", attrs={"align": "right", "bgcolor": "#cce2f3"})
                for row in rows:
                    if row.text.strip() == 'Relative standard uncertainty':
                        uncert = row.parent.findAll('b')[0].text.strip()
                        if uncert == '(exact)':
                            val.reluncert_exp = None
                            val.reluncert_man = None
                        else:
                            parts = re.split("\xa0x\xa010", uncert)
                            val.reluncert_man = parts[0]
                            val.reluncert_exp = parts[1]
                        val.save()
                        print('added ' + con.name)
            elif found.count() > 1:
                print("multiple hits!")
                print(found.values('id', 'name'))
                exit()
            else:
                print("not found!")
                print(title)
                exit()
