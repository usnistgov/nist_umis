""" example code for the datafiles app"""
import os
import django
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "umisconfig.settings")
django.setup()

from units.models import *
from django.db.models import Count


if True:
    uid = 1
    # if uid.isnumeric():
    #     try:
    #         uid = Units.objects.get(id=uid).id
    #     except Units.DoesNotExist:
    #         pass
    #         # return redirect('/')
    # elif isinstance(uid, str):
    #     try:
    #         uid = Units.objects.get(name=uid.lower()).id
    #     except Units.DoesNotExist:
    #         pass
    #         # return redirect('/')
    unit = Wdunits.objects.get(id=uid)
    clss = unit.wdclass
    qkinds = unit.quantities_set.all()
    usys = unit.unitsystem
    dvs = []
    quants = []
    types = []
    for qkind in qkinds:
        dvs.append(qkind.quantitykind.dimensionvector)
        types.append(qkind.quantitykind.type)
        for quant in qkind.quantitykind.quantities_set.all():
            quants.append(quant)
    qsys = None
    if usys.id == 1:  # if the unit system is the SI then make the quantity system the ISQ. Otherwise empty
        qsys = Quantitysystems.objects.get(id=1)
    dvs = list(set(dvs))
    dv = dvs[0]
    types = list(set(dvs))
    typ = types[0]
    quants = list(set(quants))
    data = unit.representations_set.all().filter(repsystem_id__isnull=False). \
        order_by('strng__string').exclude(repsystem__status='legacy')
    equsf = unit.equ_fromunit_related.all()
    equst = unit.equ_tounit_related.all()
    corsf = unit.cor_fromunit_related.all()
    corst = unit.cor_tounit_related.all()
    reps = {}
    for rep in data:
        sg = rep.strng.string
        if rep.repsystem_id == 15:
            sg = sg.replace('/', '-').replace('#', '%23')  # needed for IEC codes
        st = rep.strng.status
        if sg not in reps.keys():
            reps.update({sg: {'status': st, 'enccount': 0, 'strng_id': 0, 'systems': []}})
        sys = rep.repsystem
        encs = rep.strng.encodings_set.all()
        reps[sg]['enccount'] = encs.count()
        if encs.count() > 0:
            reps[sg]['strng_id'] = rep.strng.id
        tmp = {'id': sys.id, 'name': sys.name, 'abbrev': sys.abbrev, 'path': sys.path, 'encs': encs,
               'url_ep': rep.url_endpoint}
        reps[sg]['systems'].append(tmp)

if False:
    units = Units.objects.values_list('id', 'quantitykind_id').all()
    for unit in units:
        qku, created = QuantitykindsUnits.objects.get_or_create(quantitykind_id=unit[1], unit_id=unit[0])
        print(created)


if False:
    unit = Units.objects.get(id=1)
    data = unit.representations_set.all().filter(repsystem_id__isnull=False). \
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
    print(reps)


if False:
    data = Units.objects.all().order_by('quantitykind__shortname', 'name')
    byq = {}
    for unit in data:
        if unit.quantitykind.shortname not in byq.keys():
            byq.update({unit.quantitykind.shortname: []})
        tmp = {'id': unit.id, 'name': unit.name}
        byq[unit.quantitykind.shortname].append(tmp)
    print(byq)
