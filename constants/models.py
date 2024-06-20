from django.db import models


class Constants(models.Model):
    id = models.SmallAutoField(primary_key=True)
    name = models.CharField(max_length=128, blank=True, null=True)
    name_nist_2018 = models.CharField(max_length=128, blank=True, null=True)
    allnames = models.CharField(max_length=1024, blank=True, null=True)
    units_si = models.CharField(max_length=64, blank=True, null=True)
    identifier = models.CharField(max_length=128, blank=True, null=True)
    name_bipm_en = models.CharField(max_length=128, blank=True, null=True)
    name_bipm_fr = models.CharField(max_length=128, blank=True, null=True)
    ucum_constant = models.CharField(max_length=32, blank=True, null=True)
    units_ucum = models.CharField(max_length=32, blank=True, null=True)
    units_uom = models.CharField(max_length=128, blank=True, null=True)
    constant_id = models.CharField(max_length=256, blank=True, null=True)
    is_base = models.CharField(max_length=16, blank=True, null=True)
    qudt_id = models.CharField(max_length=256, blank=True, null=True)
    is_qudt = models.IntegerField(blank=True, null=True)
    is_codata = models.IntegerField(blank=True, null=True)
    is_2022 = models.IntegerField(blank=True, null=True)
    is_2018 = models.IntegerField(blank=True, null=True)
    is_2014 = models.IntegerField(blank=True, null=True)
    is_2010 = models.IntegerField(blank=True, null=True)
    is_2006 = models.IntegerField(blank=True, null=True)
    is_2002 = models.IntegerField(blank=True, null=True)
    is_1998 = models.IntegerField(blank=True, null=True)
    vercnt = models.IntegerField(blank=True, null=True)
    nistpage = models.CharField(max_length=256, blank=True, null=True)
    pagetitle = models.CharField(max_length=128, blank=True, null=True)
    symbol = models.CharField(max_length=128, blank=True, null=True)
    updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'constants'
        verbose_name_plural = "constants"

    def __str__(self):
        return f'{self.name}'


class Constantvalues(models.Model):
    id = models.SmallAutoField(primary_key=True)
    constant = models.ForeignKey(Constants, on_delete=models.PROTECT, db_column='constant_id')
    orig_name = models.CharField(max_length=128, blank=True, null=True)
    orig_value = models.CharField(max_length=64, blank=True, null=True)
    orig_uncert = models.CharField(max_length=64, blank=True, null=True)
    orig_unit = models.CharField(max_length=64, blank=True, null=True)
    value_str = models.CharField(max_length=32, blank=True, null=True)
    value_num = models.CharField(max_length=32, blank=True, null=True)
    value_man = models.CharField(max_length=16, blank=True, null=True)
    value_exp = models.IntegerField(blank=True, null=True)
    value_acc = models.PositiveIntegerField(blank=True, null=True)
    uncert_str = models.CharField(max_length=128, blank=True, null=True)
    uncert_num = models.CharField(max_length=256, blank=True, null=True)
    uncert_man = models.CharField(max_length=16, blank=True, null=True)
    uncert_exp = models.IntegerField(blank=True, null=True)
    uncert_acc = models.PositiveIntegerField(blank=True, null=True)
    reluncert_man = models.CharField(max_length=8, blank=True, null=True)
    reluncert_exp = models.IntegerField(blank=True, null=True)
    ellipsis = models.IntegerField(blank=True, null=True)
    year = models.TextField(blank=True, null=True)  # This field type is a guess.
    comments = models.CharField(max_length=256, blank=True, null=True)
    updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'constantvalues'
