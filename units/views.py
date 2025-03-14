""" views for the units app """
from django.shortcuts import render, redirect
from django.http import JsonResponse
from units.models import *

def home(request):
    """ return the homepage """
    return render(request, "../templates/home.html")


def oldindex(request):
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
    return render(request, "../templates/units/oldindex.html", {'data': data})


def index(request):
    """ new index function getting data from wikidata tables"""
    raw = Wdunits.objects.all().order_by('wdclass__quant', 'unit')
    data = {}
    for u in raw:
        # print(u.wdclass.__dict__)
        qujoins = u.wdquantswdunits_set.all()
        for qujoin in qujoins:
            quant = qujoin.wdquant.name
            if quant not in data.keys():
                data.update({quant: []})
            unit = {'id': u.id, 'name': u.unit}
            data[quant].append(unit)
    return render(request, "../templates/units/index.html", {'data': data})


def oldview(request, uid):
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
        dvs.append(qkind.quantitykind.dimensionvector.symbol)
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

    return render(request, "../templates/units/view.html",
                  {'unit': unit, 'reps': reps, 'qkinds': qkinds, 'usys': usys, 'equsf': equsf, 'equst': equst,
                   'dv': dv, 'corsf': corsf, 'corst': corst, 'qsys': qsys, 'quants': quants, 'type': typ})


def view(request, uid):
    """ view the different representations of a unit"""
    if uid.isnumeric():
        try:
            uid = Wdunits.objects.get(id=uid).id
        except Wdunits.DoesNotExist:
            return redirect('/')
    elif isinstance(uid, str):
        try:
            uid = Wdunits.objects.get(name=uid.lower()).id
        except Wdunits.DoesNotExist:
            return redirect('/')
    wdunit = Wdunits.objects.get(id=uid)
    qids = wdunit.wdquantswdunits_set.all().values_list('wdquant__quant__id', flat=True)
    dvs = wdunit.wdquantswdunits_set.all().values_list('wdquant__isq', flat=True)
    dvs = list(set(dvs))
    dv = dvs[0]
    dv = dv.replace('^', '').replace('{', '<sup>').replace('}', '</sup>').replace('\\Theta', 'Θ')
    quants = Quantities.objects.filter(id__in=qids)
    data = wdunit.representations_set.all()
    usyss = wdunit.unitsystemswdunits_set.all()
    qkinds = None
    equsf = None
    equst = None
    corsf = None
    corst = None
    qsys = None
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
                  {'unit': wdunit, 'reps': reps, 'qkinds': qkinds, 'usyss': usyss, 'equsf': equsf, 'equst': equst,
                   'dv': dv, 'corsf': corsf, 'corst': corst, 'qsys': qsys, 'quants': quants})


def search(request):
    """ search of the unit strings """
    term = request.GET.get("q")
    if term:
        hits = {'units': {}, 'quants': {}, 'reps': {}}

        # find units with term in unit name
        units = Wdunits.objects.filter(unit__icontains=term)
        if units:
            for unit in units:
                hits['units'].update({unit.id: unit.unit})

        # find quantities with the term in the name
        quants = Quantities.objects.filter(name__icontains=term)
        if quants:
            for quant in quants:
                hits['quants'].update({quant.id: quant.name})

        # find representations with the term
        if len(term) > 2:  # if long string then search as substring
            reps = Representations.objects.filter(strng__string__icontains=term)
        else:  ## ...otherwise search as exact
            reps = Representations.objects.filter(strng__string__exact=term)
        if reps:
            for rep in reps:
                hits['reps'].update({rep.wdunit_id: rep.strng.string})

        if hits:
            # if hits['units']:
            #     hits['units'] = dict(sorted(hits['units'].items(), key=lambda item: item[1]))
            # if hits['quants']:
            #     hits['quants'] = dict(sorted(hits['quants'].items(), key=lambda item: item[1]))
            # if hits['reps']:
            #     hits['reps'] = dict(sorted(hits['reps'].items(), key=lambda item: item[1]))
            return render(request, "../templates/search.html", {'hits': hits, 'term': term})
        else:
            return redirect('/')
    else:
        return redirect('/')


def crosswalk(request, sys1id=None, sys2id=None):
    """ the crosswalk endpoint for units """
    if request.method == 'POST' or (sys1id and sys2id):
        if request.method == 'POST':
            data = request.POST
            sys1id = data['sys1']
            sys2id = data['sys2']
        if not sys1id or not sys2id:
            return redirect('/')
        if sys1id == sys2id:
            return redirect('/repsystems/view/' + str(sys1id))
        site = "http://127.0.0.1/"
        # generate output dictionary
        output = {}
        # data for system 1
        rsys1 = Repsystems.objects.get(id=sys1id)
        sys1 = {'id': sys1id}
        sys1.update({'name': rsys1.name})
        sys1.update({'url': site + 'repsystems/view/' + str(sys1id)})
        # data for system 2
        rsys2 = Repsystems.objects.get(id=sys2id)
        sys2 = {'id': sys2id}
        sys2.update({'name': rsys2.name})
        sys2.update({'url': site + 'repsystems/view/' + str(sys2id)})
        # add system data
        output.update({'systems': [sys1, sys2]})
        # get a list of all units
        units = Units.objects.values('id', 'name').all()
        # get list of units in system 1
        units1 = Units.objects.filter(representations__repsystem=sys1id, representations__url_endpoint='yes'). \
            values_list('id', 'representations__strng__string')
        u1 = {}
        for uid, ustr in units1:
            u1.update({uid: ustr})
        # get list of units in system 2
        units2 = Units.objects.filter(representations__repsystem=sys2id, representations__url_endpoint='yes'). \
            values_list('id', 'representations__strng__string')
        u2 = {}
        for uid, ustr in units2:
            u2.update({uid: ustr})
        # iterate over units to find alignment
        output.update({'units': []})
        for unit in units:
            if unit['id'] in u1.keys() or unit['id'] in u2.keys():
                u = {'id': unit['id'], 'name': unit['name'], 'url': site + 'units/view/' + str(unit['id'])}
                reps = []
                if unit['id'] in u1.keys():
                    r1 = {'id': sys1id, 'string': u1[unit['id']]}
                else:
                    r1 = {'id': sys1id, 'string': 'no equivalent'}
                reps.append(r1)
                if unit['id'] in u2.keys():
                    r2 = {'id': sys2id, 'string': u2[unit['id']]}
                else:
                    r2 = {'id': sys2id, 'string': 'no equivalent'}
                reps.append(r2)
                u.update({'representations': reps})
                output['units'].append(u)

        return JsonResponse(output, safe=False)
    else:
        data = Repsystems.objects.all().values_list('id', 'name').order_by('name')
        return render(request, "../templates/units/crosswalk.html", {'data': data})


def unitimport(request):
    """ what does this do? """
    units = Units.objects.filter(representations__repsystem__id=10)
    output = {}
    output.update({'system': 'qudt'})
    output.update({'version': '2.1.24'})
    output.update({'date': '2023-02-01'})
    output.update({'units': []})
    for unit in units:
        u = {}
        u.update({'name': unit.name})
        u.update({'code': unit.representations_set.all()[0].strng.string})
        qks = unit.quantitykindsunits_set.all()
        qs = []
        for qk in qks:
            quants = qk.quantitykind.quantities_set.all()
            for quant in quants:
                qs.append(quant.name)
        sortd = qs.sort()
        u.update({'quantities': sortd})
        u.update({'status': 'current'})
        u.update({'updates': []})
        output['units'].append(u)
    return JsonResponse(output, safe=False)
