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
from dashboard.repsys_ingest import *
from datetime import date
from django.utils import timezone
from datetime import datetime
import time

# migrate data from the entities table into the representations table
ents = Entities.objects.filter(unit__isnull=False, migrated='no')
for ent in ents:
    reps = Representations.objects.filter(unit_id=ent.unit_id,
                                          repsystem_id=ent.repsystem_id, strng__string__exact=ent.value)
    if len(reps) > 1:
        print("problem!" + " (" + str(ent.id) + ")")
        exit()
    elif len(reps) == 0:
        timezone.now()
        ts = time.time()
        upd = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        print("add representation: " + str(ent.value))
        # add value to strngs table
        found = Strngs.objects.filter(string=ent.value)
        if found:
            strngid = found[0].id
        else:
            strng = Strngs(string=ent.value, status='current', autoadded='yes', updated=upd)
            strng.save()
            if not strng.id:
                print("string not saved: " + ent.value)
                exit()
            strngid = strng.id
        # lookup repsystem info for url (url_endpoint) or not
        rsurls = Repsystems.objects.filter(status='current').values_list('id', 'path')
        rsyseps = {}
        for rsid, url in rsurls:
            rsyseps.update({rsid: url})

        # add to representations table
        rep = Representations(strng_id=strngid)
        rep.unit_id = ent.unit_id
        rep.repsystem_id = ent.repsystem_id
        if rsyseps[ent.repsystem_id] is None:
            rep.url_endpoint = 'no'
        else:
            rep.url_endpoint = 'yes'
        rep.status = 'current'
        rep.checked = 'no'
        rep.updated = upd
        rep.save()
        # update migrated (entities)
        if not rep.id:
            print("representation not saved: " + ent.value)
            exit()
        else:
            print("representation saved: " + ent.value)
            ent.migrated = 'yes'
            ent.save()
    else:
        found = "representation found,"
        if reps[0].strng.string == ent.value:
            print(found + " string verified '" + ent.value + "'")
            ent.migrated = 'yes'
            ent.save()
        else:
            print(found + " string different! " + reps[0].strng.string + " | " + ent.value + " (" + str(ent.id) + ")")
