""" view file for the calculations app """
from django.shortcuts import render, redirect
from calculations.models import *
from constants.models import *
import json
from GTC import *


def index(request):
    """ return the index page """
    fqids = Equations.objects.all().values_list('fquant', flat=True).distinct()
    fqs = Quantities.objects.filter(id__in=fqids).values('id', 'name')
    fqkids = Quantities.objects.filter(id__in=fqids).values_list('quantitykind', flat=True)
    fuids = QuantitykindsUnits.objects.filter(quantitykind__in=fqkids)
    fus = Units.objects.filter(id__in=fuids).values('id', 'name')

    tqids = Equations.objects.all().values_list('tquant', flat=True).distinct()
    tqs = Quantities.objects.filter(id__in=tqids).values('id', 'name')
    tqkids = Quantities.objects.filter(id__in=tqids).values_list('quantitykind', flat=True)
    tuids = QuantitykindsUnits.objects.filter(quantitykind__in=tqkids)
    tus = Units.objects.filter(id__in=tuids).values('id', 'name')

    return render(request, "../templates/calculations/index.html", {'fqs': fqs, 'tqs': tqs, 'fus': fus, 'tus': tus})


def calculate(request, usrkey=None, calcid=None):
    """ function to calulate the requested value """
    calc = Calculations.objects.get(id=calcid)
    equ = calc.equation

    # process equation
    mathj = json.loads(equ.mathjson)  # Python list
    constants = {}
    vrs = {}
    for idx, item in enumerate(mathj):
        if "con:" in item:
            con = item.replace("con:", "")
            tmp = Constantvalues.objects.get(constant__identifier=con, year=2018)
            if not tmp.uncert_num:
                tmp.uncert_num = 0
            mathj[idx] = {"value": tmp.value_num, "uncert": tmp.uncert_num}
            constants.update({con: {"value": tmp.value_num, "uncert": tmp.uncert_num}})
        if "var:" in item:
            var = item.replace("var:", "")
            vrs.update({var: idx})

    # process data
    calcj = json.loads(calc.data)
    for key, val in calcj.items():
        if key not in vrs:
            print("incorrect variable...")
        if type(val) is str:
            # assume its a variable
            tmp = Constantvalues.objects.get(constant__identifier=val, year=2018)
            if not tmp.uncert_num:
                tmp.uncert_num = 0
            mathj[vrs[key]] = {'value': tmp.value_num, 'uncert': tmp.uncert_num}

    # execute calculation using GTC (data in mathj)
    if mathj[0] == "Multiply":
        var1 = ureal(float(mathj[1]['value']), float(mathj[1]['uncert']))
        var2 = ureal(float(mathj[2]['value']), float(mathj[2]['uncert']))
        answer = result(var1*var2)
        print("Answer: " + '{:e}'.format(answer))
        print("CODATA value: 5.4857990888(17)e-7")

    # send results
    return True


def compute(request):
    """ calculate an answer based on a question """
    sq = request.POST.get("sq")
    val = request.POST.get("val")
    su = request.POST.get("su")
    rq = request.POST.get("rq")
    ru = request.POST.get("ru")
    # find equation
    try:
        eqn = Equations.objects.filter(fquant=sq, tquant=rq)[0]
    except Equations.DoesNotExist:
        return redirect('/calculations')

    # get equation
    eqnlist = json.loads(eqn.mathjson)
    # find variables and constants
    varrs, cons = [], []
    for step in eqnlist:
        if isinstance(step, list):
            for step2 in step:
                if 'var:' in step2:
                    varrs.append(step2)
                if 'con:' in step2:
                    cons.append(step2)
        if 'var:' in step:
            varrs.append(step)
        if 'con:' in step:
            cons.append(step)

    # get values of constants
    convals = {}
    if cons:
        for con in cons:
            conid = con.replace('con:', '')
            hit = Constants.objects.get(identifier=conid)
            conval = Constantvalues.objects.get(constant_id=hit.id, year='2018')
            convals.update({conid: {'value': conval.value_num, 'uncert': conval.uncert_num}})

    # assign variables

    # calculate result using GTC, based on mathjson operations

    return render(request, "../templates/calculations/compute.html",
                  {'sq': sq, 'val': val, 'su': su, 'rq': rq, 'ru': ru, 'eqn': eqn, 'vars': varrs, 'convals': convals})
