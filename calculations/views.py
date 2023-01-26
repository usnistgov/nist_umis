from django.shortcuts import render
from calculations.models import *
from constants.models import *
import json
from GTC import *


def index(request):
    """ return the homepage """
    return render(request, "../templates/home.html")


# SELECT * FROM `constantvalues` WHERE `constant_id` IN (43,101,97) AND `year` = '2018'
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
    answer = ''
    if mathj[0] == "Multiply":
        var1 = ureal(float(mathj[1]['value']), float(mathj[1]['uncert']))
        var2 = ureal(float(mathj[2]['value']), float(mathj[2]['uncert']))
        answer = result(var1*var2)
        print("Answer: " + '{:e}'.format(answer))
        print("CODATA value: 5.4857990888(17)e-7")

    # send results
    results = "{'answer':" + str(answer) + "}"

    # TODO: output needs work...
    return JsonResponse(results, safe=False)
