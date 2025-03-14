""" search for units in OLS """
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "umisconfig.settings")
django.setup()
from ols_py.client import Ols4Client
from pytz import timezone

jax = timezone("America/New_York")

client = Ols4Client()
resp = client.search('newton per meter', params={"exact": True})
docs = resp.response.docs
hits = []
for doc in docs:
    hit = {}
    print(doc)
    hit.update({'name': doc.label})
    hit.update({'ont': doc.ontology_name})
    hit.update({'oboid': doc.obo_id})
    hits.append(hit)
print(hits)
exit()
