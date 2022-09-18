""" views for the units app """
from django.shortcuts import render, redirect
from units.models import *
from django.db.models import Count


def home(request):
    """homepage"""
    return render(request, "../templates/home.html")


def index(request):
    """ present an overview page about the system in the sds """
    data = Units.objects.all().order_by('quantitykind__shortname', 'name')
    byq = {}
    for unit in data:
        if unit.quantitykind.shortname not in byq.keys():
            byq.update({unit.quantitykind.shortname: []})
        tmp = {'id': unit.id, 'name': unit.name}
        byq[unit.quantitykind.shortname].append(tmp)
    return render(request, "../templates/units/index.html", {'data': byq})


def view(request, uid):
    if uid.isnumeric():
        pass
    elif isinstance(uid, str):
        try:
            uid = Units.objects.get(name=uid.lower()).id
        except Units.DoesNotExist:
            return redirect('/')
    unit = Units.objects.get(id=uid)
    qkind = unit.quantitykind
    usys = unit.unitsystem
    qsys = qkind.quantitysystem
    dv = qkind.dimensionvector
    quants = qkind.quantities_set.all()
    data = unit.representations_set.all().filter(repsystem_id__isnull=False).\
        annotate(count=Count('repsystem')).order_by('count')
    equsf = unit.equ_fromunit_related.all()
    equst = unit.equ_tounit_related.all()
    corsf = unit.cor_fromunit_related.all()
    corst = unit.cor_tounit_related.all()
    reps = {}
    for rep in data:
        sg = rep.strng.string
        st = rep.strng.status
        if sg not in reps.keys():
            reps.update({sg: {'status': st, 'enccount': 0, 'strng_id': 0, 'systems': []}})
        sys = rep.repsystem
        encs = rep.strng.encodings_set.all()
        reps[sg]['enccount'] = encs.count()
        if encs.count() > 0:
            reps[sg]['strng_id'] = rep.strng.id
        tmp = {'id': sys.id, 'name': sys.name, 'abbrev': sys.abbrev, 'repo': sys.repository, 'encs': encs}
        reps[sg]['systems'].append(tmp)

    return render(request, "../templates/units/view.html",
                  {'unit': unit, 'reps': reps, 'qkind': qkind, 'usys': usys, 'equsf': equsf, 'equst': equst,
                   'corsf': corsf, 'corst': corst, 'qsys': qsys, 'dv': dv, 'quants': quants})
