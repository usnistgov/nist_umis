import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "umisconfig.settings")
django.setup()

from dashboard.repsys_ingest import *
from datetime import date, datetime
from units.functions import *
from wdfunctions import *


def movereps(sys):
    repids = {"qudt": 10}
    reps = Wdunits.objects.filter(qudt__isnull=False).order_by('qudt').values_list('qudt', flat=True)
    repid = repids[sys]
    for rep in reps:
        rs = Representations.objects.filter(repsystem__id=repid).values('id', 'strng__string')
        print(rs)
        exit()


movereps("qudt")
