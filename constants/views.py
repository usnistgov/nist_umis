from django.shortcuts import render
from constants.models import *
from django.http import HttpResponse
from pnglatex import pnglatex
from umisconfig.settings import *
import json


def index(request):
    """ present an overview page about the system in the sds """
    constants = Constants.objects.all().values('id', 'name').order_by('name')
    return render(request, "../templates/constants/index.html", {'constants': constants})


def view(request, cnid):
    constant = Constants.objects.get(id=cnid)
    values = constant.constantvalues_set.all().order_by('-year')
    allvals, allaccs, allexps = [], [], []
    for i, value in enumerate(values):
        # reformat field value to display correctly
        values[i].orig_value = values[i].orig_value.replace('e', 'x 10<sup>') + '</sup>'
        if values[i].orig_uncert is not None:
            values[i].orig_uncert = values[i].orig_uncert.replace('e', 'x 10<sup>') + '</sup>'
            man = values[i].uncert_man.replace('.', '')
        else:
            man = None
        if values[i].orig_value.find(' x 10') != -1 and values[i].orig_uncert is not None:
            values[i].comments = values[i].orig_value.replace(' x 10', '(' + man + ') x 10')  # for concise form
        elif values[i].orig_uncert is not None:
            values[i].comments = values[i].orig_value + '(' + man + ')'

        if value.orig_unit == "1":
            values[i].orig_unit = ""
        allvals.append(float(value.value_num))
        allaccs.append(value.value_acc)
        allexps.append(value.value_exp)
    acc = min(allaccs) - 1
    miny = min(allvals)
    maxy = max(allvals)
    ymin = '{:.9e}'.format(miny)
    ymax = '{:.9e}'.format(maxy)
    jsdata = alldata(request, cnid)
    # TODO: https://www.youtube.com/watch?v=czt31ENbr2I  work out how to format the y axis values

    return render(request, "../templates/constants/view.html",
                  {'constant': constant, 'values': values, 'ymin': ymin, 'ymax': ymax, 'acc': acc, 'alldata': jsdata})


def jsonout(request, cnid):
    constant = dict(Constants.objects.values('identifier', 'name', 'units_si', 'nistpage', 'symbol').get(id=cnid))
    values = Constantvalues.objects.filter(constant_id=cnid).\
        values('year', 'value_num', 'uncert_num', 'orig_unit', 'reluncert_man', 'reluncert_exp').order_by('year')
    constant.update({'values': []})
    for value in values:
        constant['values'].append(dict(value))
    jfile = json.dumps(constant, default=str)
    return HttpResponse(jfile, content_type="application/json")


def alldata(request, cnid):
    constant = Constants.objects.get(id=cnid)
    condata = {'datasets': [{'label': constant.name, 'data': []}]}
    values = constant.constantvalues_set.all().order_by('year')
    data = []
    for value in values:
        xy = {'x': int(value.year), 'y': float(value.value_num)}
        data.append(xy)
    condata['datasets'][0]['data'] = data
    jfile = json.dumps(condata, default=str)
    return jfile
    # return HttpResponse(jfile, content_type="application/json")


# TODO: create image file from latex string on the fly
# TODO: this is a secrutoy risk as is
# def symbol(request, cnid):
#     sym = Constants.objects.filter(id=cnid).values('symbol')[0]
#     latex = sym['symbol'].replace('$', '')
#     ipath = STATIC_URL + 'symbols/constant' + cnid + '.png'
#     pnglatex(r"[" + latex + "]", ipath)
#     image_data = open(ipath, "rb").read()
#     return HttpResponse(image_data, mimetype="image/png")
