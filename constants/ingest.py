""" example code for the datafiles app"""
import os
import django
import csv
import re
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "umisconfig.settings")
django.setup()

from constants.models import *
from umisconfig.settings import STATIC_URL, BASE_DIR
from decimal import Decimal
from os.path import exists
from units.functions import *
from math import *


def procvalue(val, proc):
    proc.orig_value = val
    valuestr = val.replace(' ', '')
    valuestr = valuestr.replace('…', '')
    valuestr = valuestr.replace('...', '')
    proc.value_str = valuestr
    if val.find('e') != -1:
        valueacc = valuestr.index('e') - 1
    else:
        valueacc = len(re.findall('[0-9]', valuestr))
    proc.value_acc = valueacc
    if valuestr.find('.') == -1:
        dp = 0
    else:
        dp = 1
    scinot = '%.' + str(valueacc - dp) + 'e'  # https://stackoverflow.com/questions/6913532/
    valuenum = scinot % Decimal(valuestr)
    proc.value_num = valuenum
    parts = valuenum.split("e")
    proc.value_man = parts[0]
    proc.value_exp = int(parts[1])
    return


def procuncert(unc, proc):
    # calculate uncertainties and add to proc
    if unc == 'null' or unc == '(exact)':
        proc.uncert_str = None
        proc.uncert_num = None
        proc.uncert_man = None
        proc.uncert_exp = None
        proc.uncert_acc = None
    else:
        proc.orig_uncert = unc
        uncertstr = unc.replace(' ', '')
        proc.uncert_str = uncertstr
        if uncertstr.find('0e') != -1:  # check for a trailing zero
            tzero = '0'
        else:
            tzero = ''
        if '(exact)' in uncertstr:
            floatstr = None
        else:
            floatval = float(uncertstr)
            floatstr = str(floatval)
        if tzero == '0':
            uncertnum = floatstr.replace('e', '.0e')
        else:
            uncertnum = floatstr
        proc.uncert_num = uncertnum

        if uncertnum is None:
            parts = [None, None]
        elif uncertnum.find('e') != -1:
            parts = uncertnum.split("e")
        elif float(uncertnum) < 1:  # float returns decimal value not value in sci notation
            ulen = len(uncertnum)
            expn = -1
            for j in range(2, ulen-1):
                if uncertnum[j] == '0':
                    expn = expn - 1
            acc = len(uncertnum) - 2
            man = str(float(uncertnum) * pow(10, -1 * expn))[0:acc+1]
            parts = [man, str(expn)]
        else:
            parts = [uncertnum, 0]
        proc.uncert_man = parts[0]
        if parts[1]:
            proc.uncert_exp = int(parts[1])
        else:
            proc.uncert_exp = None
        if parts[0]:
            proc.uncert_acc = len(parts[0]) - 1  # lose one for decimal point
        else:
            proc.uncert_acc = None

        # # calculate the relative uncertainty
        # reluncert = float(proc.uncert_num)/float(proc.value_num)
        # relacc = proc.uncert_acc
        # uparts = str(reluncert).split("e")
        # proc.reluncert_man = uparts[0][0:relacc+1]
        # proc.reluncert_exp = int(uparts[1])

    return


years = ['2022']
for year in years:
    path = str(BASE_DIR) + '/' + STATIC_URL + 'imports/allascii_' + year + '.txt'

    if not exists(path):
        continue

    with open(path) as f:
        reader = csv.reader(f, delimiter="\t")
        consts = list(reader)

    ntmp = Constants.objects.all().values_list('allnames', flat=True)
    names = []
    for nam in ntmp:
        nlist = json.loads(nam)
        for nitem in nlist:
            names.append(nitem)

    for const in consts:
        # print(const)
        name = const[0]
        # check if constant has been added
        check = Constantvalues.objects.filter(orig_name=name, year=year)
        if check.count() == 1:
            print("found " + name)
            continue
        data = {}
        # check if its three columns of data (uncert at end) or four (just process)
        if len(const) == 3:
            const.append(const[2])  # move unit to column 4 (index 3)
            if const[1].find('(') == -1:
                const[2] = 'null'
            else:
                # split value and uncertainty
                const[2] = const[1]
                # remove uncertainty from value
                const[1] = re.sub(r'\(\d+\)', '', const[1])
                # reformat uncertaintly correct based on value
                const[2] = re.sub(r'\d{2}\(', '(', const[2])  # remove the two digits to the left of the uncertainty
                const[2] = const[2].replace(' ', '')  # remove spaces
                const[2] = re.sub(r'\d+\.', '0.', const[2])
                for i in range(2, len(const[2])):
                    if const[2][i].isdigit():
                        const[2] = const[2][:i] + '0' + const[2][i+1:]  # change digit to zero (as string)
                    elif const[2][i] == '(':
                        const[2] = const[2].replace('(', '')  # remove left parens
                        break
                const[2] = const[2].replace(')', '')  # remove right parens
        # save new constant data
        conval = Constantvalues()
        conval.orig_name = name
        conval.year = year
        # check for ellipsis
        if const[1].find('…') != -1 or const[1].find('...') != -1:
            ell = 1
            const[1] = const[1].replace('…', '').replace('...', '')
        else:
            ell = 0
        conval.ellipsis = ell
        # process the value
        procvalue(const[1], conval)
        # process the uncertainty
        procuncert(const[2], conval)
        # add the unit
        if const[3] == '':
            conval.orig_unit = '1'
        else:
            conval.orig_unit = const[3]

        # find constant and add id
        if name in names:
            con = Constants.objects.filter(allnames__contains=name)[0]
        else:
            print("new constant - " + name)
            exit()
        conval.constant_id = con.id
        # save constantvalue
        conval.updated = getds()
        conval.save()

        # update constant for year based version
        match year:
            case '2022':
                con.is_2022 = 1
            case '2018':
                con.is_2018 = 1
            case '2014':
                con.is_2014 = 1
            case '2010':
                con.is_2010 = 1
            case '2006':
                con.is_2006 = 1
            case '2002':
                con.is_2002 = 1
            case '1998':
                con.is_1998 = 1

        # update constant table
        con.updated = getds()
        con.save()
        print("added " + name)
