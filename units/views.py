""" views for the units app """
from django.shortcuts import render, redirect
from units.models import *


def home(request):
    """ return the homepage """
    return render(request, "../templates/home.html")


def index(request):
    """ present an overview page about the system in the sds """
    data = Units.objects.all().order_by('quantitykindsunits__quantitykind__name', 'name')
    byq = {}
    unitids = {}
    for unit in data:
        qkinds = unit.quantitykindsunits_set.all()
        for qkind in qkinds:
            if qkind.quantitykind.name not in byq.keys():
                byq.update({qkind.quantitykind.name: []})
                unitids.update({qkind.quantitykind.name: []})
            if unit.id not in unitids[qkind.quantitykind.name]:
                tmp = {'id': unit.id, 'name': unit.name}
                unitids[qkind.quantitykind.name].append(unit.id)
                byq[qkind.quantitykind.name].append(tmp)
    # sort by key (order by in units call does not work because of multiple qkinds per unit possible)
    tmp2 = list(byq.keys())
    tmp2.sort()
    data = {i: byq[i] for i in tmp2}
    return render(request, "../templates/units/index.html", {'data': data})


def view(request, uid):
    """ view the different representations of a unit"""
    if uid.isnumeric():
        try:
            uid = Units.objects.get(id=uid).id
        except Units.DoesNotExist:
            return redirect('/')
    elif isinstance(uid, str):
        try:
            uid = Units.objects.get(name=uid.lower()).id
        except Units.DoesNotExist:
            return redirect('/')
    unit = Units.objects.get(id=uid)
    qkinds = unit.quantitykindsunits_set.all()
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
    type = types[0]
    quants = list(set(quants))
    data = unit.representations_set.all().filter(repsystem_id__isnull=False).\
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

    return render(request, "../templates/units/view.html",
                  {'unit': unit, 'reps': reps, 'qkinds': qkinds, 'usys': usys, 'equsf': equsf, 'equst': equst,
                   'dv': dv, 'corsf': corsf, 'corst': corst, 'qsys': qsys, 'quants': quants, 'type': type})


def search(request):
    term = request.GET.get("q")
    if term:
        strngs = Strngs.objects.filter(string=term).values_list(id, flat=True)
        if strngs:
            units = Units.objects.select_related('representations').get(representations__strng_id__in=strngs)
            if len(units) == 1:
                unit = units[0]
                return redirect('/units/view/' + str(unit.id))
            else:
                return render(request, "../templates/search.html", {'units': units, 'term': term})
        else:
            return redirect('/')
    else:
        return redirect('/')
