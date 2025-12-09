""" example code for the datafiles app"""
import os
import django
import csv
import re
import requests
from bs4 import BeautifulSoup
from selenium import webdriver

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from quantities.models import *

driver = webdriver.Firefox()
driver.get('https://www.iso.org/obp/ui#iso:std:iso:80000:-9:ed-2:v1:en')
html = driver.page_source
data = BeautifulSoup(html, 'html.parser')
print(data)
quants = data.find_all(id='toc_iso_std_iso_80000-9_ed-2_v1_en_sec_3')
print(quants)
