""" views for the units app """
from django.shortcuts import render, redirect
from django.contrib import messages
from units.models import *
from umisconfig.settings import *
from django.http import JsonResponse, HttpResponse
from .forms import SearchForm

import datetime

site = "http://127.0.0.1:"


def home(request):
    """ information page about the API """
    # include the search form...
    form = SearchForm()
    return render(request, '../templates/api/home.html', {'form': form})


def spec(request):
    """ redirect to the OpenAPI page on Swaggerhub """
    return redirect("https://app.swaggerhub.com/apis-docs/stuchalk/nist-umis/1.1.0")


def unitslist(request):
    """ API endpoint for the list of units """
    data = Units.objects.all()
    output = {}
    output.update({"title": "List of UMIS Units"})
    output.update({"apiurl": site + "api/units/list/"})
    output.update({"apiversion": "1.1.0"})
    output.update({"retrieved": datetime.datetime.now()})
    units = []
    for datum in data:
        u = {}
        u.update({"id": datum.id})
        u.update({"name": datum.name})
        u.update({"url": site + "units/view/" + str(datum.id)})
        units.append(u)
    output.update({'units': units})
    return JsonResponse(output, safe=False)


def unitview(request, uid=None):
    """ API endpoint for individual unit by id or name """
    if not uid:
        # redirect to the API home page if no unit identifier given
        return redirect('/api/home')
    # check for value unit by name or id
    opts = Units.objects.all().values_list('name', flat=True)
    if uid not in opts:
        if uid.isnumeric():
            try:
                uid = Units.objects.get(id=uid).name
                return redirect('/api/units/view/' + uid)
            except Prefixes.DoesNotExist:
                return redirect('/')
        elif isinstance(uid, str):
            try:
                uid = Units.objects.get(name=uid.lower()).name
                return redirect('/api/units/view/' + uid)
            except Prefixes.DoesNotExist:
                return redirect('/')

    unit = Units.objects.filter(name=uid)[0]
    reps = Representations.objects.filter(unit_id=unit.id, repsystem_id__isnull=False, repsystem__status='current')
    output = {}
    output.update({"name": unit.name})
    output.update({"description": unit.description})
    output.update({"unittype": unit.type})
    output.update({"url": site + "units/view/" + uid})
    output.update({"apiurl": site + "api/units/view/" + uid})
    output.update({"apiversion": "1.1.0"})
    output.update({"retrieved": datetime.datetime.now()})
    rs = []
    for rep in reps:
        r = {"id": rep.repsystem_id}
        r.update({"string": rep.strng.string})
        r.update({"repsystem": rep.repsystem.name})
        if rep.url_endpoint == 'yes':
            r.update({"repsystemurl": rep.repsystem.path + rep.strng.string})
        rs.append(r)
    output.update({"representations": rs})
    return JsonResponse(output, safe=False)


def search(request):
    """ API endpoint for unit search by strng value """
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SearchForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            if not form.cleaned_data['term']:
                # redirect to the API home page if no unit identifier given
                messages.add_message(request, messages.INFO, 'No term entered!')
                return redirect('/api/')
            # search the strings in the strngs table - look for exact match
            hits = Strngs.objects.filter(string=form.cleaned_data['term'])  # filter avoids not found error
            if hits:
                # get the first hit and rdirect to the unit API...
                hit = hits[0]
                reps = Representations.objects.filter(strng_id=hit.id)
                return redirect('/api/units/view/' + str(reps[0].unit_id))
            else:
                messages.add_message(request, messages.INFO, 'No unit found!')
                return redirect('/api/')
        else:
            # redirect to the API home page if no unit identifier given
            messages.add_message(request, messages.INFO, 'Invalid term!')
            return redirect('/api/')
