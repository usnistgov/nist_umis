from django.db import models


class Quantitysystems(models.Model):
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=1024)
    abbrev = models.CharField(max_length=16)
    url = models.CharField(max_length=256)
    updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'quantitysystems'


class Dimensionvectors(models.Model):
    name = models.CharField(max_length=2048)
    description = models.CharField(max_length=1024)
    dim_exp_l = models.DecimalField(db_column='dim_exp_L', max_digits=2, decimal_places=1)  # Field name made lowercase.
    dim_exp_m = models.DecimalField(db_column='dim_exp_M', max_digits=2, decimal_places=1)  # Field name made lowercase.
    dim_exp_t = models.DecimalField(db_column='dim_exp_T', max_digits=2, decimal_places=1)  # Field name made lowercase.
    dim_exp_i = models.DecimalField(db_column='dim_exp_I', max_digits=2, decimal_places=1)  # Field name made lowercase.
    dim_exp_h = models.DecimalField(db_column='dim_exp_H', max_digits=2, decimal_places=1)  # Field name made lowercase.
    dim_exp_n = models.DecimalField(db_column='dim_exp_N', max_digits=2, decimal_places=1)  # Field name made lowercase.
    dim_exp_j = models.DecimalField(db_column='dim_exp_J', max_digits=2, decimal_places=1)  # Field name made lowercase.
    dim_exp_d = models.DecimalField(db_column='dim_exp_D', max_digits=2, decimal_places=1)  # Field name made lowercase.
    shortcode = models.CharField(max_length=32, blank=True, null=True)
    longcode = models.CharField(max_length=128, blank=True, null=True)
    symbol = models.CharField(max_length=512)
    basesi_shortcode = models.CharField(max_length=512, blank=True, null=True)
    basesi_longcode = models.CharField(max_length=512, blank=True, null=True)
    quantitysystem = models.ForeignKey(Quantitysystems, on_delete=models.PROTECT, db_column='quantitysystem_id')
    updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'dimensionvectors'


class Quantitykinds(models.Model):
    id = models.SmallAutoField(primary_key=True)
    name = models.CharField(max_length=128)
    shortname = models.CharField(max_length=128, blank=True, null=True)
    type = models.CharField(max_length=16, blank=True, null=True)
    description = models.CharField(max_length=1024, blank=True, null=True)
    symbol = models.CharField(max_length=64)
    shortcode = models.CharField(max_length=128, blank=True, null=True)
    baseunit_id = models.IntegerField(blank=True, null=True)
    quantitysystem = models.ForeignKey(Quantitysystems, on_delete=models.PROTECT, db_column='quantitysystem_id')
    dimensionvector = models.ForeignKey(Dimensionvectors, on_delete=models.PROTECT, db_column='dimensionvector_id')
    updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'quantitykinds'


class Unitsystems(models.Model):
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=1024)
    abbrev = models.CharField(max_length=16)
    quantitysystem = models.ForeignKey(Quantitysystems, on_delete=models.PROTECT, db_column='quantitysystem_id')
    url = models.CharField(max_length=256)
    updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'unitsystems'


class Units(models.Model):
    name = models.CharField(max_length=128)
    unitsystem = models.ForeignKey(Unitsystems, on_delete=models.PROTECT, db_column='unitsystem_id')
    description = models.CharField(max_length=1024, blank=True, null=True)
    prefix_id = models.IntegerField(blank=True, null=True)
    factor_id = models.SmallIntegerField(blank=True, null=True)
    url = models.CharField(max_length=256, blank=True, null=True)
    type = models.CharField(max_length=19, blank=True, null=True)
    shortcode = models.CharField(max_length=512, blank=True, null=True)
    alt_shortcode = models.CharField(max_length=512, blank=True, null=True)
    ivoa = models.CharField(max_length=512, blank=True, null=True)
    html = models.CharField(max_length=256, blank=True, null=True)
    text = models.CharField(max_length=128, blank=True, null=True)
    text_si = models.CharField(db_column='text_SI', max_length=128, blank=True, null=True)  # Field name made lowercase.
    updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'units'
        app_label = 'units'
        verbose_name_plural = "units"

    def __str__(self):
        return f'{self.name}'


class Domains(models.Model):
    title = models.CharField(max_length=64)
    type = models.CharField(max_length=32)
    description = models.CharField(max_length=512)
    updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'domains'
        verbose_name_plural = "domains"

    def __str__(self):
        return f'{self.title}'


class Quantities(models.Model):
    id = models.SmallAutoField(primary_key=True)
    quantitykind = models.ForeignKey(Quantitykinds, on_delete=models.PROTECT, db_column='quantitykind_id')
    quantitysystem = models.ForeignKey(Quantitysystems, on_delete=models.PROTECT, db_column='quantitysystem_id')
    name = models.CharField(max_length=128)
    altnames = models.CharField(max_length=512)
    description = models.CharField(max_length=1024, blank=True, null=True)
    symbol = models.CharField(max_length=128, blank=True, null=True)
    latexsymbol = models.CharField(max_length=512, blank=True, null=True)
    latexdefn = models.CharField(max_length=512, blank=True, null=True)
    url = models.CharField(max_length=256, blank=True, null=True)
    domain_id = models.IntegerField(blank=True, null=True)
    updated = models.DateTimeField()
    sysml_name = models.CharField(max_length=128, blank=True, null=True)
    sysml_domain = models.CharField(max_length=32, blank=True, null=True)
    sysml_defn = models.CharField(max_length=512, blank=True, null=True)
    sysml_symbol = models.CharField(max_length=32, blank=True, null=True)
    sysml_numtype = models.CharField(max_length=128, blank=True, null=True)
    sysml_unittype = models.CharField(max_length=128, blank=True, null=True)
    sysml_torder = models.IntegerField(blank=True, null=True)
    sysml_qdim = models.CharField(max_length=64, blank=True, null=True)
    sysml_unit = models.CharField(max_length=128, blank=True, null=True)
    sysml_remark = models.CharField(max_length=256, blank=True, null=True)
    iso_source = models.CharField(max_length=256, blank=True, null=True)
    iso_item = models.CharField(max_length=8, blank=True, null=True)
    done = models.CharField(max_length=3)

    class Meta:
        managed = False
        db_table = 'quantities'


class Repsystems(models.Model):
    name = models.CharField(max_length=128)
    abbrev = models.CharField(max_length=16, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    version = models.CharField(max_length=32, blank=True, null=True)
    type = models.CharField(max_length=13, blank=True, null=True)
    status = models.CharField(max_length=7, blank=True, null=True)
    url = models.CharField(max_length=256, blank=True, null=True)
    repository = models.CharField(max_length=256, blank=True, null=True)
    path = models.CharField(max_length=256, blank=True, null=True)
    domain = models.ForeignKey(Domains, on_delete=models.PROTECT, db_column='domain_id')
    fileupdated = models.DateField()
    fileformat = models.CharField(max_length=8, blank=True, null=True)
    checked = models.DateTimeField()
    jsondata = models.TextField(blank=True, null=True)
    updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'repsystems'
        verbose_name_plural = "repsystems"

    def __str__(self):
        return f'{self.name}'


class Strngs(models.Model):
    name = models.CharField(max_length=128, blank=True, null=True)
    string = models.CharField(max_length=512)
    status = models.CharField(max_length=11, blank=True, null=True)
    reason = models.CharField(max_length=128, blank=True, null=True)
    autoadded = models.CharField(max_length=3)
    updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'strngs'


class Encodings(models.Model):
    strng = models.ForeignKey(Strngs, on_delete=models.PROTECT, db_column='strng_id')
    string = models.CharField(max_length=512)
    format = models.CharField(max_length=7)
    updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'encodings'


class Representations(models.Model):
    unit = models.ForeignKey(Units, on_delete=models.PROTECT, db_column='unit_id')
    quantity = models.ForeignKey(Quantities, on_delete=models.PROTECT, db_column='quantity_id')
    unitsystem = models.ForeignKey(Unitsystems, on_delete=models.PROTECT, db_column='unitsystem_id')
    repsystem = models.ForeignKey(Repsystems, on_delete=models.PROTECT, db_column='repsystem_id')
    strng = models.ForeignKey(Strngs, on_delete=models.PROTECT, db_column='strng_id')
    url_endpoint = models.CharField(max_length=3, blank=True, null=True)
    status = models.CharField(max_length=7, blank=True, null=True)
    checked = models.CharField(max_length=3)
    updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'representations'
        unique_together = (('unit_id', 'repsystem_id', 'strng_id'),)


class Prefixes(models.Model):
    name = models.CharField(max_length=32, db_collation='utf8_unicode_ci')
    symbol = models.CharField(max_length=64, db_collation='utf8_unicode_ci')
    value = models.CharField(max_length=32, db_collation='utf8_unicode_ci')
    inverse = models.CharField(max_length=32, db_collation='utf8_unicode_ci', blank=True, null=True)
    quantitysystem = models.ForeignKey(Quantitysystems, on_delete=models.PROTECT, db_column='quantitysystem_id')
    updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'prefixes'


class Equivalents(models.Model):
    fromunit = models.ForeignKey(Units, on_delete=models.PROTECT, db_column='from_unit',
                                 related_name="equ_fromunit_related")
    tounit = models.ForeignKey(Units, on_delete=models.PROTECT, db_column='to_unit', related_name="equ_tounit_related")
    factor = models.FloatField(blank=True, null=True)
    prefix = models.ForeignKey(Prefixes, on_delete=models.PROTECT, db_column='prefix_id')
    # constant = models.ForeignKey(Constants, on_delete=models.PROTECT, db_column='constant_id')
    updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'equivalents'


class Factors(models.Model):
    id = models.SmallAutoField(primary_key=True)
    name = models.CharField(max_length=128)
    nunit = models.ForeignKey(Units, on_delete=models.PROTECT, db_column='nunit_id', related_name="nunit_related")
    dunit = models.ForeignKey(Units, on_delete=models.PROTECT, db_column='dunit_id', related_name="dunit_related")
    nfactor = models.CharField(max_length=16)
    dfactor = models.CharField(max_length=16)
    exact = models.CharField(max_length=3)
    sf = models.IntegerField(blank=True, null=True)
    updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'factors'


class Correspondents(models.Model):
    fromunit = models.ForeignKey(Units, on_delete=models.PROTECT, db_column='from_unit',
                                 related_name="cor_fromunit_related")
    tounit = models.ForeignKey(Units, on_delete=models.PROTECT, db_column='to_unit', related_name="cor_tounit_related")
    factor = models.FloatField(blank=True, null=True)
    factoreqn = models.CharField(max_length=64, blank=True, null=True)
    prefix = models.ForeignKey(Prefixes, on_delete=models.PROTECT, db_column='prefix_id')
    # constant = models.ForeignKey(Constants, on_delete=models.PROTECT, db_column='constant_id')
    updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'correspondents'


class Dimensions(models.Model):
    id = models.SmallAutoField(primary_key=True)
    quantitysystem = models.ForeignKey(Quantitysystems, on_delete=models.PROTECT, db_column='quantitysystem_id')
    name = models.CharField(max_length=128)
    type = models.CharField(max_length=64)
    symbol = models.CharField(max_length=256)
    qudtstring = models.CharField(max_length=128)
    updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'dimensions'


class Entities(models.Model):
    unit = models.ForeignKey('Units', models.DO_NOTHING, blank=True, null=True, db_column='unit_id')
    repsys = models.CharField(max_length=16)
    repsystem = models.ForeignKey(Repsystems, on_delete=models.PROTECT, db_column='repsystem_id')
    name = models.CharField(max_length=64, blank=True, null=True)
    lang = models.CharField(max_length=16, blank=True, null=True)
    symbol = models.CharField(max_length=128, blank=True, null=True)
    quantity = models.CharField(max_length=1024, blank=True, null=True)
    quantityid = models.CharField(max_length=1024, blank=True, null=True)
    value = models.CharField(max_length=128, blank=True, null=True)
    source = models.CharField(max_length=32, blank=True, null=True)
    comment = models.CharField(max_length=1024, blank=True, null=True)
    migrated = models.CharField(max_length=3, blank=True, null=True)
    lastupdate = models.DateField(blank=True, null=True)
    updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'entities'


class QuantitykindsUnits(models.Model):
    quantitykind = models.ForeignKey(Quantitykinds, on_delete=models.PROTECT, db_column='quantitykind_id')
    unit = models.ForeignKey(Units, on_delete=models.PROTECT, db_column='unit_id')
    updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'quantitykinds_units'
