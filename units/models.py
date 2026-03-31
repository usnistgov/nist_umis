from django.db import models


class Quantitysystems(models.Model):
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=1024)
    abbrev = models.CharField(max_length=16)
    url = models.CharField(max_length=256)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'quantitysystems'
        db_table_comment = 'Table of systems of quanitites (e.g. SI)'
        app_label = 'units'


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
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'dimensionvectors'
        db_table_comment = 'Table of dimension vectors'
        app_label = 'units'

    def __str__(self):
        return f'{self.shortcode}'


class Quantitykinds(models.Model):
    id = models.SmallAutoField(primary_key=True)
    name = models.CharField(max_length=128)
    shortname = models.CharField(max_length=128, blank=True, null=True)
    type = models.CharField(max_length=16, blank=True, null=True)
    description = models.CharField(max_length=1024, blank=True, null=True)
    symbol = models.CharField(max_length=64)
    shortcode = models.CharField(max_length=128, blank=True, null=True)
    baseunit_id = models.IntegerField(blank=True, null=True)
    quantitysystem = models.ForeignKey(Quantitysystems, on_delete=models.PROTECT, db_column='quantitysystem_id',
                                       blank=True, null=True)
    dimensionvector = models.ForeignKey(Dimensionvectors, on_delete=models.PROTECT, db_column='dimensionvector_id',
                                        blank=True, null=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'quantitykinds'
        db_table_comment = 'Table of quantity kinds'
        app_label = 'units'

    def __str__(self):
        return f'{self.name}'


class Unitsystems(models.Model):
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=1024)
    abbrev = models.CharField(max_length=16)
    wdurl = models.CharField(max_length=128, blank=True, null=True)
    quantitysystem = models.ForeignKey(Quantitysystems, on_delete=models.PROTECT, db_column='quantitysystem_id')
    url = models.CharField(max_length=256)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'unitsystems'
        db_table_comment = 'Table of unit systems'
        app_label = 'units'

    def __str__(self):
        return f'{self.name}'


class Units(models.Model):
    class UnitTypes(models.TextChoices):
        """ choice for status field """
        ACCEPTEDNONSI = 'Accepted Non-SI', 'Accepted Non-SI'
        CGSBASE = 'CGS Base', 'CGS Base'
        OTHER = 'Other', 'Other'
        SIBASE = 'SI Base', 'SI Base'
        SICOHDERIVED = 'SI Coherent Derived', 'SI Coherent Derived'
        SIDERIVED = 'SI Derived', 'SI Derived'
        SISPECIALNAME = 'SI Special Named', 'SI Special Named'
        USCUSTOMARY = 'US Customary', 'US Customary'

    name = models.CharField(max_length=128)
    unitsystem = models.ForeignKey(Unitsystems, on_delete=models.PROTECT, db_column='unitsystem_id')
    description = models.CharField(max_length=1024, blank=True, null=True)
    prefix = models.ForeignKey('Prefixes', on_delete=models.PROTECT, blank=True, null=True, db_column='prefix_id')
    factor_id = models.SmallIntegerField(blank=True, null=True)
    url = models.CharField(max_length=256, blank=True, null=True)
    type = models.CharField(max_length=19, choices=UnitTypes, default=UnitTypes.SIDERIVED, blank=True, null=True)
    shortcode = models.CharField(max_length=512, blank=True, null=True)
    alt_shortcode = models.CharField(max_length=512, blank=True, null=True)
    ivoa = models.CharField(max_length=512, blank=True, null=True)
    html = models.CharField(max_length=256, blank=True, null=True)
    text = models.CharField(max_length=128, blank=True, null=True)
    text_si = models.CharField(db_column='text_SI', max_length=128, blank=True, null=True)  # Field name made lowercase.
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'units'
        db_table_comment = 'Table of units'
        app_label = 'units'
        verbose_name_plural = "units"

    def __str__(self):
        return f'{self.name}'


class Domains(models.Model):
    title = models.CharField(max_length=64)
    type = models.CharField(max_length=32)
    description = models.CharField(max_length=512)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'domains'
        db_table_comment = 'Table of disciplinary domains'
        verbose_name_plural = "domains"
        app_label = 'units'

    def __str__(self):
        return f'{self.title}'


class Quantities(models.Model):
    id = models.SmallAutoField(primary_key=True)
    quantitykind = models.ForeignKey(Quantitykinds, on_delete=models.PROTECT, db_column='quantitykind_id')
    quantitysystem = models.ForeignKey(Quantitysystems, on_delete=models.PROTECT, db_column='quantitysystem_id')
    name = models.CharField(max_length=128)
    altnames = models.CharField(max_length=512)
    sysnames = models.CharField(max_length=512, blank=True, null=True)
    description = models.CharField(max_length=1024, blank=True, null=True)
    symbol = models.CharField(max_length=128, blank=True, null=True)
    latexsymbol = models.CharField(max_length=512, blank=True, null=True)
    latexdefn = models.CharField(max_length=512, blank=True, null=True)
    url = models.CharField(max_length=256, blank=True, null=True)
    domain_id = models.IntegerField(blank=True, null=True)
    updated = models.DateTimeField(auto_now=True)
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
        ordering = ('name',)
        db_table = 'quantities'
        db_table_comment = 'Table of quantities'
        app_label = 'units'

    def __str__(self):
        return f'{self.name}'


class Repsystems(models.Model):
    name = models.CharField(max_length=128)
    abbrev = models.CharField(max_length=16, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    version = models.CharField(max_length=32, blank=True, null=True)
    type = models.CharField(max_length=13, blank=True, null=True)
    status = models.CharField(max_length=7, blank=True, null=True)
    site = models.CharField(max_length=256, blank=True, null=True)
    repo = models.CharField(max_length=256, blank=True, null=True)
    src = models.CharField(max_length=256, blank=True, null=True)
    path = models.CharField(max_length=256, blank=True, null=True)
    domain = models.ForeignKey(Domains, on_delete=models.PROTECT, db_column='domain_id')
    fileupdated = models.DateField()
    fileformat = models.CharField(max_length=8, blank=True, null=True)
    checked = models.DateTimeField()
    rawdata = models.TextField(blank=True, null=True)
    jsondata = models.TextField(blank=True, null=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'repsystems'
        db_table_comment = 'Table of representation systems'
        verbose_name_plural = "repsystems"
        app_label = 'units'

    def __str__(self):
        return f'{self.name}'


class Strngs(models.Model):
    name = models.CharField(max_length=128, blank=True, null=True)
    string = models.CharField(max_length=512)
    status = models.CharField(max_length=11, blank=True, null=True)
    reason = models.CharField(max_length=128, blank=True, null=True)
    autoadded = models.CharField(max_length=3)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'strngs'
        verbose_name_plural = "Strings"
        ordering = ('string',)
        db_table_comment = 'Table of text strings'
        app_label = 'units'

    def __str__(self):
        return f'{self.string}'


class Encodings(models.Model):
    strng = models.ForeignKey(Strngs, on_delete=models.PROTECT, db_column='strng_id')
    string = models.CharField(max_length=512)
    format = models.CharField(max_length=7)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'encodings'
        db_table_comment = 'Table of encodings'
        app_label = 'units'


class Prefixes(models.Model):
    name = models.CharField(max_length=32, db_collation='utf8_unicode_ci')
    symbol = models.CharField(max_length=64, db_collation='utf8_unicode_ci')
    value = models.CharField(max_length=32, db_collation='utf8_unicode_ci')
    inverse = models.CharField(max_length=32, db_collation='utf8_unicode_ci', blank=True, null=True)
    quantitysystem = models.ForeignKey(Quantitysystems, on_delete=models.PROTECT, db_column='quantitysystem_id')
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'prefixes'
        db_table_comment = 'Table of prefixes'
        app_label = 'units'

    def __str__(self):
        return f'{self.name}'


class Equivalents(models.Model):
    fromunit = models.ForeignKey(Units, on_delete=models.PROTECT, db_column='from_unit',
                                 related_name="equ_fromunit_related")
    tounit = models.ForeignKey(Units, on_delete=models.PROTECT, db_column='to_unit', related_name="equ_tounit_related")
    factor = models.FloatField(blank=True, null=True)
    prefix = models.ForeignKey(Prefixes, on_delete=models.PROTECT, db_column='prefix_id')
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'equivalents'
        db_table_comment = 'Table of equivalents'
        app_label = 'units'


class Factors(models.Model):
    id = models.SmallAutoField(primary_key=True)
    name = models.CharField(max_length=128)
    nunit = models.ForeignKey(Units, on_delete=models.PROTECT, db_column='nunit_id', related_name="nunit_related")
    dunit = models.ForeignKey(Units, on_delete=models.PROTECT, db_column='dunit_id', related_name="dunit_related")
    nfactor = models.CharField(max_length=16)
    dfactor = models.CharField(max_length=16)
    exact = models.CharField(max_length=3)
    sf = models.IntegerField(blank=True, null=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'factors'
        db_table_comment = 'Table of factors'
        app_label = 'units'


class Correspondents(models.Model):
    fromunit = models.ForeignKey(Units, on_delete=models.PROTECT, db_column='from_unit',
                                 related_name="cor_fromunit_related")
    tounit = models.ForeignKey(Units, on_delete=models.PROTECT, db_column='to_unit', related_name="cor_tounit_related")
    factor = models.FloatField(blank=True, null=True)
    factoreqn = models.CharField(max_length=64, blank=True, null=True)
    prefix = models.ForeignKey(Prefixes, on_delete=models.PROTECT, db_column='prefix_id')
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'correspondents'
        db_table_comment = 'Table of correspondents'
        app_label = 'units'


class Dimensions(models.Model):
    id = models.SmallAutoField(primary_key=True)
    quantitysystem = models.ForeignKey(Quantitysystems, on_delete=models.PROTECT, db_column='quantitysystem_id')
    name = models.CharField(max_length=128)
    type = models.CharField(max_length=64)
    symbol = models.CharField(max_length=256)
    qudtstring = models.CharField(max_length=128)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'dimensions'
        db_table_comment = 'Table of dimensions'
        app_label = 'units'


class Entities(models.Model):
    unit = models.ForeignKey('Units', on_delete=models.PROTECT, blank=True, null=True, db_column='unit_id')
    repsys = models.CharField(max_length=16)
    repsystem = models.ForeignKey(Repsystems, on_delete=models.PROTECT, db_column='repsystem_id', blank=True, null=True)
    name = models.CharField(max_length=64, blank=True, null=True)
    lang = models.CharField(max_length=16, blank=True, null=True)
    symbol = models.CharField(max_length=128, blank=True, null=True)
    quantity = models.CharField(max_length=1024, blank=True, null=True)
    quantityid = models.CharField(max_length=1024, blank=True, null=True)
    value = models.CharField(max_length=128, blank=True, null=True)
    source = models.CharField(max_length=32, blank=True, null=True)
    comment = models.CharField(max_length=1024, blank=True, null=True)
    migrated = models.CharField(max_length=3, blank=True, null=True)
    lastcheck = models.DateField(blank=True, null=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'entities'
        db_table_comment = 'Table of entities'
        app_label = 'units'


class QuantitykindsUnits(models.Model):
    quantitykind = models.ForeignKey(Quantitykinds, on_delete=models.PROTECT, db_column='quantitykind_id')
    unit = models.ForeignKey(Units, on_delete=models.PROTECT, db_column='unit_id')
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'quantitykinds_units'
        db_table_comment = 'Join table of quantitykinds and units'
        app_label = 'units'


class EntitiesQuantities(models.Model):
    entity = models.ForeignKey(Entities, on_delete=models.PROTECT, db_column='entity_id')
    quantity = models.ForeignKey(Units, on_delete=models.PROTECT, db_column='quantity_id')
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'entities_quantities'
        db_table_comment = 'Table of quantities associated to unit entities'
        app_label = 'units'


class Wdclasses(models.Model):
    name = models.CharField(max_length=128, blank=True, null=True)
    url = models.CharField(max_length=128, blank=True, null=True)
    isq = models.CharField(max_length=128, blank=True, null=True)
    source = models.CharField(max_length=128, blank=True, null=True)
    section = models.CharField(max_length=16, blank=True, null=True)
    quant = models.CharField(max_length=128, blank=True, null=True)
    quantity = models.ForeignKey(Quantities, on_delete=models.PROTECT, db_column='quantity_id', blank=True, null=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'wdclasses'
        verbose_name_plural = "Wikidata Unit Classes"
        ordering = ('name',)
        db_table_comment = 'Table of Wikidata Unit Classes'
        app_label = 'units'

    def __str__(self):
        return f'{self.name}'


class Wdsiclasses(models.Model):
    curl = models.CharField(max_length=128)
    label = models.CharField(max_length=32)
    silabel = models.CharField(max_length=32, blank=True, null=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'wdsiclasses'
        verbose_name_plural = "Wikidata SI Unit Classes"
        db_table_comment = 'Table of wikidata SI related classes'
        app_label = 'units'

    def __str__(self):
        return f'{self.label}'


class Wdunits(models.Model):
    unit = models.CharField(max_length=64, blank=True, null=True)
    sitype = models.ForeignKey(Wdsiclasses, on_delete=models.PROTECT, db_column='sitype', blank=True, null=True)
    wdclass = models.ForeignKey(Wdclasses, on_delete=models.PROTECT, db_column='wdclass_id', blank=True, null=True)
    cls = models.CharField(db_column='class', max_length=64, blank=True, null=True)  # Field renamed reserved word.
    quant = models.CharField(max_length=32, blank=True, null=True)
    factor = models.CharField(max_length=256, blank=True, null=True)
    wdfacunit = models.ForeignKey('self', on_delete=models.PROTECT, db_column='wdfacunit_id', blank=True, null=True)
    curl = models.CharField(max_length=128, blank=True, null=True)
    uurl = models.CharField(max_length=128, blank=True, null=True)
    qurl = models.CharField(max_length=128, blank=True, null=True)
    status = models.CharField(max_length=7, blank=True, null=True)
    found = models.CharField(max_length=3, blank=True, null=True)
    added = models.DateField(auto_now_add=True)
    comment = models.CharField(max_length=256, blank=True, null=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        ordering = ['unit']
        verbose_name_plural = "Wikidata Units"
        db_table = 'wdunits'
        db_table_comment = 'Table of unit representations on Wikidata'
        app_label = 'units'

    def __str__(self):
        return f'{self.unit}'


class Wdquants(models.Model):
    id = models.SmallAutoField(primary_key=True)
    quant = models.ForeignKey(Quantities, on_delete=models.PROTECT, db_column='quantity_id', blank=True, null=True)
    # quantity_id = models.SmallIntegerField(blank=True, null=True)
    qurl = models.CharField(max_length=64, blank=True, null=True)
    name = models.CharField(max_length=128, blank=True, null=True)
    isq = models.CharField(max_length=32, blank=True, null=True)
    source = models.CharField(max_length=128, blank=True, null=True)
    sect = models.CharField(max_length=16, blank=True, null=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'wdquants'
        verbose_name_plural = "Wikidata Quantities"
        db_table_comment = 'Table of wikidata quantities'
        app_label = 'units'


class Representations(models.Model):
    class Checked(models.TextChoices):
        """ choice for checked field """
        YES = 'yes', 'Yes'
        NO = 'no', 'No'

    class Status(models.TextChoices):
        """ choice for status field """
        ALTERNATE = 'alternate', 'Alternate'
        CURRENT = 'current', 'Current'
        DEFINITIVE = 'definitive', 'Definitive'
        DELETED = 'deleted', 'Deleted'
        DISCOURAGED = 'discouraged', 'Discouraged'
        LEGACY = 'legacy', 'Legacy'
        PREFERRED = 'preferred', 'Preferred'
        UNKNOWN = 'unknown', 'Unknown'

    unit = models.ForeignKey(Units, on_delete=models.PROTECT, db_column='unit_id', blank=True, null=True)
    wdunit = models.ForeignKey(Wdunits, on_delete=models.PROTECT, db_column='wdunit_id', blank=True, null=True)
    repsystem = models.ForeignKey(Repsystems, on_delete=models.PROTECT, db_column='repsystem_id', blank=True, null=True)
    strng = models.ForeignKey(Strngs, on_delete=models.PROTECT, db_column='strng_id', blank=True, null=True)
    status = models.CharField(max_length=16, choices=Status, default=Status.UNKNOWN)
    checked = models.CharField(max_length=3, choices=Checked, default=Checked.NO)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'representations'
        db_table_comment = 'Table of unit representations'
        unique_together = (('unit_id', 'repsystem_id', 'strng_id'),)
        verbose_name_plural = "representations"
        app_label = 'units'

    def __str__(self):
        return f'{self.strng.string}'


class WdquantsWdunits(models.Model):
    wdquant = models.ForeignKey(Wdquants, on_delete=models.PROTECT)
    wdunit = models.ForeignKey(Wdunits, on_delete=models.PROTECT)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'wdquants_wdunits'
        unique_together = (('id', 'wdquant'),)
        db_table_comment = 'Join table between wikidata quantities and units'
        app_label = 'units'


class UnitsystemsWdunits(models.Model):
    unitsystem = models.ForeignKey(Unitsystems, on_delete=models.PROTECT)
    wdunit = models.ForeignKey(Wdunits, on_delete=models.PROTECT)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'unitsystems_wdunits'
        db_table_comment = 'Join table for wdunits and unitsystems'
        app_label = 'units'
