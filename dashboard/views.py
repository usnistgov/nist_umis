from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from units.models import Repsystems
from config.settings import *
# from repsystems.scripts import *
from datetime import datetime
import requests
import mimetypes
import pytz


def checkrepsystem(request, rsid):
    """ checks a repsystem for its location and any update """
    rtrn = ""
    if rsid == 15:
        repsysobj = Repsystems.objects.get(id=rsid)
        repsys = Repsystems.objects.values('id', 'url').filter(id == rsid)
        req = requests.get(repsys['url'])
        if req.status_code != '200':
            return "website cannot be found"
        ctype = req.headers['Content-type']
        ext = mimetypes.guess_extension(ctype,)
        # TODO: add check for existing file and comparison of bytes
        with open(os.path.join(BASE_DIR, STATIC_URL, f'repsys_{rsid}{ext}'), 'wb') as f:
            f.write(req.content)
            f.close()
        # check for file update -> format of req['Last-Modified'] is "Mon, 10 Oct 2022 20:32:55 GMT"
        rdate = datetime.strptime(req.headers['Last-Modified'], '%a, %d %b %Y %H:%M:%S %Z').date()
        ldate = repsys['fileupdated']

        if ldate is None:
            repsysobj.fileupdated = rdate
            rtrn = "added"
        elif ldate < rdate:
            repsysobj.fileupdated = rdate
            rtrn = "updated"
        else:
            rtrn = "file unchanged"
        # add the time this was run
        pyjax = pytz.timezone("America/New_York")
        repsysobj.checked = pyjax.localize(datetime.now())
        repsysobj.save()
    elif rsid == 10:
        """ QUDT """

    return rtrn


def getrepsysunits(request, rsid):
    """
    scrape the data for this repsystem and store it (as json) in the jsondata field in the repsystems table
    format of data for each unit should be
    """
    print(rsid)  # needed?
    exit()


def view(request):
    # get data about the different repsystems
    reps = Repsystems.objects.all()
    return render(request, "../templates/dashboard/view.html", {'reps': reps})


def overview(request):
    """ generate page showing current status of the system """
    repsyss = Repsystems.objects.filter(status='current').order_by('name')
    return render(request, "../templates/dashboard/overview.html", {'repsyss': repsyss})


@csrf_exempt
def dashajax(request):
    # check whether the request is ajax request and whether the method is post
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        rdata = request.POST
        out = None
        if rdata['action'] == 'update':
            # run the update script for repsys
            out = runqudt()
        jresp = {'data': {'bytes': out}, 'status': 'success', 'message': ''}
        return JsonResponse(jresp)

    return JsonResponse({"error": "Not AJAX request or Wrong request method"}, status=500)
