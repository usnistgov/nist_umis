import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "umisconfig.settings")
django.setup()

from dashboard.repsys_ingest import *
from units.functions import *

local = timezone("America/New_York")


def movereps(sys):
    repsysids = {"qudt": 10}
    repsysid = repsysids[sys]
    wtmp = Wdunits.objects.filter(qudt__isnull=False).order_by('qudt').values_list('id', 'qudt')
    wunts = {}
    for w in wtmp:
        wunts.update({w[0]: w[1]})
    # check each unit
    count = 0
    for wdid, wunt in wunts.items():
        count += 1
        rs = (Representations.objects.filter(repsystem__id=repsysid, strng__string=wunt).
              values('strng_id', 'strng__string'))
        # update the representation table
        if rs:
            if len(rs) > 1:
                print('multiple unit string!')
                print(rs)
                exit()
            # add wunit id to the representations table
            strid = rs[0]['strng_id']
            rep = Representations.objects.get(repsystem__id=repsysid, strng_id=strid)
            rep.wdunit_id = wdid
            rep.save()
            print("linked wdunit " + wunt)
            # remove entry (clean) from the wdunits table
            w = Wdunits.objects.get(id=wdid)
            if sys == "qudt":
                w.qudt = None
            w.save()
        else:
            print("no matches: " + str(wunt))
            dt = local.localize(datetime.now())
            # add to strngs table
            strng = Strngs(string=wunt, status='current', autoadded='yes', updated=dt)
            strng.save()
            # add to representations table
            urlep = None
            if sys == "qudt":
                urlep = 'yes'
            newrep = Representations(wdunit_id=wdid, repsystem_id=repsysid, strng_id=strng.id,
                                     url_endpoint=urlep, status='current', checked='no', updated=dt)
            newrep.save()
            print("added wdunit " + wunt)
            # remove entry (clean) from the wdunits table
            w = Wdunits.objects.get(id=wdid)
            if sys == "qudt":
                w.qudt = None
            w.save()
        if count > 4:
            exit()
    exit()


movereps("qudt")
