""" calculation related models """
from django.db import models
from units.models import *


class Equations(models.Model):
    """ model for the equations table """
    id = models.SmallAutoField(primary_key=True)
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=128)
    mathjson = models.CharField(max_length=1024)
    fquant = models.ForeignKey(Quantities, on_delete=models.PROTECT, db_column='from_quant', related_name='fquant')
    tquant = models.ForeignKey(Quantities, on_delete=models.PROTECT, db_column='to_quant', related_name='tquant')
    comments = models.CharField(max_length=256)
    updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'equations'


class Calculations(models.Model):
    """ model for the calculations table """
    request = models.CharField(max_length=128)
    equation = models.ForeignKey(Equations, on_delete=models.PROTECT, db_column='equation_id')
    data = models.CharField(max_length=1024)
    comments = models.CharField(max_length=256)
    updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'calculations'
