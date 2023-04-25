""" example code for the calculations app"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "umisconfig.settings")
django.setup()

from calculations.views import *


calculate(1)
