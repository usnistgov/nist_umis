""" example code for the datafiles app"""
import os
import django
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "umisconfig.settings")
django.setup()

from units.models import *
from django.db.models import Count

unit = Units.objects.get(id=1)
data = unit.representations_set.all().filter(repsystem_id__isnull=False).\
    annotate(count=Count('repsystem_id')).order_by('count')
equsf = unit.equ_fromunit_related.all()
equst = unit.equ_tounit_related.all()
corsf = unit.cor_fromunit_related.all()
corst = unit.cor_tounit_related.all()
reps = {}
for rep in data:
    sg = rep.strng.string
    st = rep.strng.status
    if sg not in reps.keys():
        reps.update({sg: {'status': st, 'systems': []}})
    sys = rep.repsystem
    tmp1 = rep.strng.encodings_set.all()
    encs = tmp1.count()
    tmp2 = {'id': sys.id, 'name': sys.name, 'abbrev': sys.abbrev, 'repo': sys.repository, 'encs': encs}
    reps[sg]['systems'].append(tmp2)
print(equ)


# data = Units.objects.all().order_by('quantitykind__shortname', 'name')
# byq = {}
# for unit in data:
#     if unit.quantitykind.shortname not in byq.keys():
#         byq.update({unit.quantitykind.shortname: []})
#     tmp = {'id': unit.id, 'name': unit.name}
#     byq[unit.quantitykind.shortname].append(tmp)
# print(byq)
