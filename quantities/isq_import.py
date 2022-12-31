""" file to import ISO quantity definitions """
import django
import json
import os
import re

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "umisconfig.settings")
django.setup()

from units.models import *
from django.db.models import Count
from umisconfig.settings import STATIC_URL, BASE_DIR

# get the ISO Quantities from SysML files

path = str(BASE_DIR) + '/' + STATIC_URL + 'sysml/ISQThermodynamics.sysml'
with open(path) as fp:
    Lines = fp.readlines()
    quants = []
    ignore = []
    for lnum, line in enumerate(Lines):
        # detect start of quantity definition
        if re.search(r'/\* (?:ISO|IEC)-80000', line):
            # look ahead to find the end of definition, capture these lines in ignore for outer loop
            quant = [line]
            lines = 1
            while not re.search(r'}', Lines[lnum + lines]):
                quant.append(Lines[lnum + lines])
                lines += 1
            ignore.append(lnum + lines)
            quant.append(Lines[lnum + lines])
            quants.append(quant)
    # process quantities
    for quant in quants:
        name, qdim = "", ""
        for line in quant:
            if re.search(r'\* quantity dimension: ', line):
                src = re.search(r"\* quantity dimension: (.+?)\n", line)
                if src:
                    qdim = src.groups()[0]
            elif re.search(r'\* (?:ISO|IEC)-80000', line):
                src = re.search(r"\* (?:ISO|IEC)-80000-\d+ item \d+-\d+\.?\d?\d? (.+?)\*/\n", line)
                if src:
                    name = src.groups()[0]

        # find if entry already in table
        found = Quantities.objects.filter(sysml_qdim=qdim, name=name)
        if not found:
            newq = Quantities(quantitysystem_id=1, name=name, sysml_qdim=src.groups()[0], done='no')
        else:
            newq = found[0]

        # already in DB?
        if newq.done == 'yes':
            print(newq.name + " already added")
            continue
        for line in quant:
            if re.search(r'\* (?:ISO|IEC)-80000', line):
                src = re.search(r"\* ((?:ISO|IEC)-80000-\d+) item (\d+-\d+\.?\d?\d?) .*?\*/\n", line)
                if src:
                    newq.iso_source = src.groups()[0]
                    newq.iso_item = src.groups()[1]
            elif re.search(r"\* symbol\(s\): ", line):
                src = re.search(r"\* symbol\(s\): `(.+?)`", line)
                if src:
                    newq.sysml_symbol = src.groups()[0]
            elif re.search(r"\* name: ", line):
                src = re.search(r"\* name: (.+?)\n", line)
                if src:
                    newq.sysml_name = src.groups()[0]
            elif re.search(r"\* measurement unit\(s\): ", line):
                src = re.search(r"\* measurement unit\(s\): (.+?)\n", line)
                if src:
                    newq.sysml_unit = src.groups()[0]
            elif re.search(r"\* tensor order: ", line):
                src = re.search(r"\* tensor order: (.+?)\n", line)
                if src:
                    newq.sysml_torder = src.groups()[0]
            elif re.search(r"\* definition: ", line):
                src = re.search(r"\* definition: (.+?)\n", line)
                if src:
                    newq.sysml_defn = src.groups()[0]
            elif re.search(r"\* remarks: ", line):
                src = re.search(r"\* remarks: (.+?)\n", line)
                if src:
                    newq.sysml_remark = src.groups()[0]
            elif re.search(r"\* application domain: ", line):
                src = re.search(r"\* application domain: (.+?)\n", line)
                if src:
                    newq.sysml_domain = src.groups()[0]
            elif re.search(r"attribute :>> num: ", line):
                src = re.search(r"attribute :>> num: (.+?);\n", line)
                if src:
                    newq.sysml_numtype = src.groups()[0]
            elif re.search(r"attribute :>> mRef: ", line):
                src = re.search(r"attribute :>> mRef: (.+?);\n", line)
                if src:
                    newq.sysml_unittype = src.groups()[0]
        newq.done = 'yes'
        newq.save()
        print(newq.name + " added")
