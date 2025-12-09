import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from dashboard.repsys_ingest import *
from units.functions import *

local = timezone("America/New_York")


# move reps from wdunits table to the representations table as links
def movereps(sys):
    """ move reps from wdunits table to the representations table as links """
    repsysids = {"qudt": 10, "iev": 21, "igb": 3, "ncit": 9, "ucum": 2, "unece": 6, "uom": 13, "wolf": 20, "wur": 23}
    repsysid = repsysids[sys]
    wtmp = None
    fn__isnull = sys + "__isnull"
    # search for varible as field name uses ** construct below
    wtmp = Wdunits.objects.filter(**{fn__isnull: False}).order_by(sys).values_list('id', sys)
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
            rep.onwd = 'yes'
            rep.save()
            print(str(count) + " linked wdunit " + wunt)
        else:
            # check if the string is already in the strngs table but associated with another repsystem
            strngs = Strngs.objects.filter(string=wunt)
            dt = local.localize(datetime.now())
            if not strngs:
                print("no matches: " + wunt)
                # add to strngs table
                strng = Strngs(string=wunt, status='current', autoadded='yes', updated=dt)
                strng.save()
                if strng.id:
                    print("added string: " + wunt)
                else:
                    print(wunt + " not added as string!")
                    exit()
            else:
                strng = strngs[0]
            # add to representations table
            urlep = 'no'
            if sys in ["qudt", "iev", "igb", "ncit", "uom"]:
                urlep = 'yes'
            newrep = Representations(wdunit_id=wdid, repsystem_id=repsysid, strng_id=strng.id,
                                     url_endpoint=urlep, status='current', onwd='yes', checked='no', updated=dt)
            newrep.save()
            if newrep.id:
                print(str(count) + " added wdunit: " + wunt)
            else:
                print(wunt + " not added as representation!")
                exit()

        # remove entry (clean) from the wdunits table
        w = Wdunits.objects.get(id=wdid)
        # update field based on variable for field name uses setattr function
        setattr(w, sys, None)
        w.save()

        if count > 299:
            exit()
    exit()


movereps("wur")
