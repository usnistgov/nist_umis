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
    reps = Representations.objects.filter(unit_id=ent.unit_id, repsystem_id=ent.repsystem_id)
    if len(reps) > 1:
        print("problem!")
        exit()
    elif len(reps) == 0:
        print("add representation")
    else:
        print("representation found")
        if reps[0].strng.string == ent.value:
            print("string verified")
            # update checked and migrated

        else:
            print("string different! " + reps[0].strng.string + " | " + ent.value)
    exit()
