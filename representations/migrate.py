import json
import os
import django
import requests
import mimetypes
import re
import pytz

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "umisconfig.settings")
django.setup()
from units.models import *
from umisconfig.settings import *
from bs4 import BeautifulSoup
from datetime import datetime
from dashboard.repsys_ingest import *
from datetime import date


# migrate data from the entities table into the representations table
ents = Entities.objects.filter(unit__isnull=False)
for ent in ents:
    reps = Representations.objects.filter(unit_id=ent.unit_id,
                                          repsystem_id=ent.repsystem_id, strng__string__exact=ent.value)
    if len(reps) > 1:
        print("problem!" + " (" + str(ent.id) + ")")
        exit()
    elif len(reps) == 0:
        print("add representation: " + str(ent.value))
        # add value to strngs table
        found = Strngs.objects.filter(string=ent.value)
        if found:
            strngid = found.id
        else:
            strng = Strngs(string=ent.value, status='current', autoadded='yes')
            strng.save()
            if not strng.id:
                print("string not saved: " + ent.value)
                exit()
            strngid = strng.id
        # add to representations table
        rep = Representations(strng_id=strngid)
        rep.unit_id = ent.unit_id
        rep.repsystem_id = ent.repsystem_id
        rep.status = 'current'
        rep.checked = 'no'
        rep.save()
        # update migrated (entities)
        if not rep.id:
            print("representation not saved: " + ent.value)
        else:
            print("representation saved: " + ent.value)
            exit()
        exit()
    else:
        found = "representation found,"
        if reps[0].strng.string == ent.value:
            print(found + " string verified '" + ent.value + "'")
        else:
            print(found + " string different! " + reps[0].strng.string + " | " + ent.value + " (" + str(ent.id) + ")")
