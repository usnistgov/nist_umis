""" models for unitsystem specific tables"""
from units.models import *


class Qudtunits(models.Model):
    name = models.CharField(max_length=64, blank=True, null=True)
    code = models.CharField(max_length=32, blank=True, null=True)
    dimvector = models.CharField(max_length=128, blank=True, null=True)
    siexact = models.CharField(max_length=32, blank=True, null=True)
    defunitsystems = models.CharField(max_length=128, blank=True, null=True)
    dercohsystems = models.CharField(max_length=128, blank=True, null=True)
    derunitsystems = models.CharField(max_length=512, blank=True, null=True)
    multiplier = models.CharField(max_length=256, blank=True, null=True)
    omunit = models.CharField(max_length=256, blank=True, null=True)
    ieccodes = models.CharField(max_length=128, blank=True, null=True)
    ucumcodes = models.CharField(max_length=128, blank=True, null=True)
    unececodes = models.CharField(max_length=16, blank=True, null=True)
    symbol = models.CharField(max_length=64, blank=True, null=True)
    normrefs = models.CharField(max_length=1024, blank=True, null=True)
    infrefs = models.CharField(max_length=1024, blank=True, null=True)
    description = models.CharField(max_length=2048, blank=True, null=True)
    altlabel = models.CharField(max_length=64, blank=True, null=True)
    dbpedia = models.CharField(max_length=256, blank=True, null=True)
    latexsymbol = models.CharField(max_length=128, blank=True, null=True)
    unit = models.ForeignKey(Units, models.DO_NOTHING, db_column='unit_id')
    updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'qudtunits'
        db_table_comment = 'Table of QUDT unit entries'
        app_label = 'qudtunits'


class Qudtqkinds(models.Model):
    code = models.CharField(max_length=64, blank=True, null=True)
    description = models.CharField(max_length=2048, blank=True, null=True)
    dimvector = models.CharField(max_length=64, blank=True, null=True)
    ddimvector = models.CharField(max_length=64, blank=True, null=True)
    ndimvector = models.CharField(max_length=64, blank=True, null=True)
    dims = models.CharField(max_length=512, blank=True, null=True)
    basedims = models.CharField(max_length=256, blank=True, null=True)
    basecgsdims = models.CharField(max_length=256, blank=True, null=True)
    baseimpdims = models.CharField(max_length=256, blank=True, null=True)
    baseisodims = models.CharField(max_length=256, blank=True, null=True)
    basesidims = models.CharField(max_length=256, blank=True, null=True)
    baseusdims = models.CharField(max_length=256, blank=True, null=True)
    labels = models.CharField(max_length=256, blank=True, null=True)
    altlabels = models.CharField(max_length=512, blank=True, null=True)
    latexdefn = models.CharField(max_length=1024, blank=True, null=True)
    latexsymb = models.CharField(max_length=128, blank=True, null=True)
    symbols = models.CharField(max_length=128, blank=True, null=True)
    nrefs = models.CharField(max_length=1024, blank=True, null=True)
    infrefs = models.CharField(max_length=1024, blank=True, null=True)
    isorefs = models.CharField(max_length=1024, blank=True, null=True)
    matches = models.CharField(max_length=512, blank=True, null=True)
    cmatches = models.CharField(max_length=512, blank=True, null=True)
    urls = models.CharField(max_length=512, blank=True, null=True)
    siunits = models.CharField(max_length=256, blank=True, null=True)
    broader = models.CharField(max_length=512, blank=True, null=True)
    sameas = models.CharField(max_length=1024, blank=True, null=True)
    seealso = models.CharField(max_length=512, blank=True, null=True)
    comesfrom = models.CharField(max_length=512, blank=True, null=True)
    abbrevs = models.CharField(max_length=512, blank=True, null=True)
    comments = models.CharField(max_length=1024, blank=True, null=True)
    updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'qudtqkinds'
        db_table_comment = 'Table of QUDT unit entries'
        app_label = 'qudtqkinds'


class QudtqkindsQudtunits(models.Model):
    qudtqkind = models.ForeignKey(Qudtqkinds, models.DO_NOTHING)
    qudtunit = models.ForeignKey(Qudtunits, models.DO_NOTHING)
    updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'qudtqkinds_qudtunits'
        db_table_comment = 'Join table for qudt units a qkinds'
        app_label = 'qudtqkinds_qudtunits'


class UnitsystemsQudtunits(models.Model):
    unitsystem = models.ForeignKey(Unitsystems, models.DO_NOTHING, blank=True, null=True)
    qudtunit = models.ForeignKey(Qudtunits, models.DO_NOTHING)
    updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'unitsystems_qudtunits'
        db_table_comment = 'Join table for qudt units a quantity systems'
        app_label = 'unitsystems_qudtunits'
