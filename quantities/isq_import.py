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

path = str(BASE_DIR) + '/' + STATIC_URL + 'sysml/ISQAcoustics.sysml'
with open(path) as fp:
    Lines = fp.readlines()
    quants = []
    ignore = []
    for lnum, line in enumerate(Lines):
        # detect start of quantity definition
        if re.search(r'/\* ISO-80000', line):
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
        print(json.dumps(quant, indent=True))
        exit()