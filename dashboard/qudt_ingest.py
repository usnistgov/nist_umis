import json
import os
import django
import requests
import mimetypes
import re
import pytz

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "umisconfig.settings")
django.setup()
from units.models import *
from umisconfig.settings import *
from bs4 import BeautifulSoup
from datetime import datetime
from dashboard.repsys_ingest import getrepsystemdata
from datetime import date


def qudtingest():
    repsys = Repsystems.objects.values('id', 'url', 'fileformat').get(id=10)
    # TODO: add file exists check and download
    ext = repsys['fileformat']
    with open(os.path.join(BASE_DIR, STATIC_URL, f'repsys_10_data{ext}'), 'r') as f:
        tmp = f.read()
        f.close()

