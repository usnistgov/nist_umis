from django.db import models


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
    REPLACED = 'replaced', 'Replaced'
    UNKNOWN = 'unknown', 'Unknown'


class Quantitysystems(models.Model):
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=1024, null=True)
    abbrev = models.CharField(max_length=16, null=True)
    url = models.CharField(max_length=256, null=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'quantitysystems'
        db_table_comment = 'Table of systems of quanitites (e.g. SI)'
        app_label = 'units'


class Dimensionvectors(models.Model):
    name = models.CharField(max_length=2048)
    description = models.CharField(max_length=1024, null=True)
    dim_exp_l = models.DecimalField(db_column='dim_exp_L', max_digits=2, decimal_places=1, default=0)  # Field name made lowercase.
    dim_exp_m = models.DecimalField(db_column='dim_exp_M', max_digits=2, decimal_places=1, default=0)  # Field name made lowercase.
    dim_exp_t = models.DecimalField(db_column='dim_exp_T', max_digits=2, decimal_places=1, default=0)  # Field name made lowercase.
    dim_exp_i = models.DecimalField(db_column='dim_exp_I', max_digits=2, decimal_places=1, default=0)  # Field name made lowercase.
    dim_exp_h = models.DecimalField(db_column='dim_exp_H', max_digits=2, decimal_places=1, default=0)  # Field name made lowercase.
    dim_exp_n = models.DecimalField(db_column='dim_exp_N', max_digits=2, decimal_places=1, default=0)  # Field name made lowercase.
    dim_exp_j = models.DecimalField(db_column='dim_exp_J', max_digits=2, decimal_places=1, default=0)  # Field name made lowercase.
    dim_exp_d = models.DecimalField(db_column='dim_exp_D', max_digits=2, decimal_places=1, default=0)  # Field name made lowercase.
    shortcode = models.CharField(max_length=32, null=True)
    longcode = models.CharField(max_length=128, null=True)
    symbol = models.CharField(max_length=512, null=True)
    basesi_shortcode = models.CharField(max_length=512, null=True)
    basesi_longcode = models.CharField(max_length=512, null=True)
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
    name = models.CharField(max_length=128)
    shortname = models.CharField(max_length=128, null=True)
    type = models.CharField(max_length=16, null=True)
    description = models.CharField(max_length=1024, null=True)
    symbol = models.CharField(max_length=64, null=True)
    shortcode = models.CharField(max_length=128, null=True)
    baseunit_id = models.IntegerField(null=True)
    quantitysystem = models.ForeignKey(Quantitysystems, on_delete=models.PROTECT, db_column='quantitysystem_id', null=True)
    dimensionvector = models.ForeignKey(Dimensionvectors, on_delete=models.PROTECT, db_column='dimensionvector_id', null=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'quantitykinds'
        ordering = ('name',)
        db_table_comment = 'Table of quantity kinds'
        app_label = 'units'

    def __str__(self):
        return f'{self.name}'


class Unitsystems(models.Model):
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=1024, null=True)
    abbrev = models.CharField(max_length=16, null=True)  # these are the QUDT SOU names
    wdurl = models.CharField(max_length=128, null=True)
    quantitysystem = models.ForeignKey(Quantitysystems, on_delete=models.PROTECT, db_column='quantitysystem_id')
    url = models.CharField(max_length=256, null=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'unitsystems'
        db_table_comment = 'Table of unit systems'
        app_label = 'units'

    def __str__(self):
        return f'{self.name}'


class Units(models.Model):
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=1024, null=True)
    prefix = models.ForeignKey('Prefixes', on_delete=models.PROTECT, null=True, db_column='prefix_id')
    factor = models.ForeignKey('Factors', on_delete=models.PROTECT, null=True, db_column='factor_id')
    # factor_id = models.SmallIntegerField(null=True)
    url = models.CharField(max_length=256, null=True)
    type = models.CharField(max_length=19, choices=UnitTypes, default=UnitTypes.SIDERIVED, null=True)
    shortcode = models.CharField(max_length=512, null=True)
    alt_shortcode = models.CharField(max_length=512, null=True)
    ivoa = models.CharField(max_length=512, null=True)
    html = models.CharField(max_length=256, null=True)
    text = models.CharField(max_length=128, null=True)
    text_si = models.CharField(db_column='text_SI', max_length=128, null=True)  # Field name made lowercase.
    usysts = models.ManyToManyField(Unitsystems, through='UnitsUnitsystems')
    qkinds = models.ManyToManyField(Quantitykinds, through='QuantitykindsUnits')
    checked = models.CharField(max_length=3, choices=Checked, default=Checked.NO)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'units'
        db_table_comment = 'Table of units'
        ordering = ('name',)
        app_label = 'units'
        verbose_name_plural = "units"

    def __str__(self):
        return f'{self.name}'


class UnitSynonyms(models.Model):
    synonym = models.CharField(max_length=128, unique=True, null=True)
    unit = models.ForeignKey(Units, on_delete=models.PROTECT, db_column='unit_id', null=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'units_synonyms'
        db_table_comment = 'Table of unit synonyms'
        ordering = ('synonym',)
        app_label = 'units'
        verbose_name_plural = "Unit synonyms"

    def __str__(self):
        return f'{self.synonym}'


class UnitsUnitsystems(models.Model):
    unit = models.ForeignKey(Units, on_delete=models.PROTECT, db_column='unit_id')
    usys = models.ForeignKey(Unitsystems, on_delete=models.PROTECT, db_column='usys_id')
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'units_unitsystems'
        unique_together = (('unit_id', 'usys_id'),)
        db_table_comment = 'Join table between units and unit systems'
        app_label = 'units'


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
    quantitykind = models.ForeignKey(Quantitykinds, on_delete=models.PROTECT, db_column='quantitykind_id')
    quantitysystem = models.ForeignKey(Quantitysystems, on_delete=models.PROTECT, db_column='quantitysystem_id')
    qudtkind = models.ForeignKey('Qudtqkinds', on_delete=models.PROTECT, db_column='qudtqkind_id', null=True)
    name = models.CharField(max_length=128)
    altnames = models.CharField(max_length=512, null=True)
    sysnames = models.CharField(max_length=512, null=True)
    description = models.CharField(max_length=1024, null=True)
    symbol = models.CharField(max_length=128, null=True)
    latexsymbol = models.CharField(max_length=512, null=True)
    latexdefn = models.CharField(max_length=512, null=True)
    url = models.CharField(max_length=256, null=True)
    domain_id = models.IntegerField(null=True)
    updated = models.DateTimeField(auto_now=True)
    sysml_name = models.CharField(max_length=128, null=True)
    sysml_domain = models.CharField(max_length=32, null=True)
    sysml_defn = models.CharField(max_length=512, null=True)
    sysml_symbol = models.CharField(max_length=32, null=True)
    sysml_numtype = models.CharField(max_length=128, null=True)
    sysml_unittype = models.CharField(max_length=128, null=True)
    sysml_torder = models.IntegerField(null=True)
    sysml_qdim = models.CharField(max_length=64, null=True)
    qudt_qdim = models.CharField(max_length=64, null=True)
    sysml_unit = models.CharField(max_length=128, null=True)
    sysml_remark = models.CharField(max_length=256, null=True)
    iso_source = models.CharField(max_length=256, null=True)
    iso_item = models.CharField(max_length=8, null=True)
    done = models.CharField(max_length=3)

    class Meta:
        managed = False
        ordering = ('name',)
        db_table = 'quantities'
        db_table_comment = 'Table of quantities'
        app_label = 'units'

    def __str__(self):
        return f'{self.name}'

# update from here
class Repsystems(models.Model):
    name = models.CharField(max_length=128)
    abbrev = models.CharField(max_length=16, null=True)
    description = models.TextField(null=True)
    version = models.CharField(max_length=32, null=True)
    type = models.CharField(max_length=13, null=True)
    status = models.CharField(max_length=7, null=True)
    site = models.CharField(max_length=256, null=True)
    repo = models.CharField(max_length=256, null=True)
    src = models.CharField(max_length=256, null=True)
    path = models.CharField(max_length=256, null=True)
    domain = models.ForeignKey(Domains, on_delete=models.PROTECT, db_column='domain_id')
    fileupdated = models.DateField()
    fileformat = models.CharField(max_length=8, null=True)
    checked = models.DateTimeField()
    validator = models.CharField(max_length=256, null=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        ordering = ['name']
        db_table = 'repsystems'
        db_table_comment = 'Table of representation systems'
        verbose_name_plural = "repsystems"
        app_label = 'units'

    def __str__(self):
        return f'{self.name}'


class Strngs(models.Model):
    name = models.CharField(max_length=128, null=True)
    string = models.CharField(max_length=512, null=True)
    status = models.CharField(max_length=11, choices=Status, default=Status.UNKNOWN, null=True)
    reason = models.CharField(max_length=128, null=True)
    autoadded = models.CharField(max_length=3, choices=Checked, default=Checked.YES, null=True)
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
    string = models.CharField(max_length=512, null=True)
    format = models.CharField(max_length=7, null=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'encodings'
        db_table_comment = 'Table of encodings'
        app_label = 'units'


class Prefixes(models.Model):
    name = models.CharField(max_length=32)
    symbol = models.CharField(max_length=64, null=True)
    value = models.CharField(max_length=32, null=True)
    inverse = models.CharField(max_length=32, null=True)
    quantitysystem = models.ForeignKey(Quantitysystems, on_delete=models.PROTECT, db_column='quantitysystem_id')
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'prefixes'
        db_table_comment = 'Table of prefixes'
        app_label = 'units'

    def __str__(self):
        return f'{self.name}'


class Factors(models.Model):
    name = models.CharField(max_length=128)
    code = models.CharField(max_length=4)
    nunit = models.ForeignKey(Units, on_delete=models.PROTECT, db_column='nunit_id', related_name="nunit_related", null=True)
    dunit = models.ForeignKey(Units, on_delete=models.PROTECT, db_column='dunit_id', related_name="dunit_related", null=True)
    uncert = models.CharField(max_length=128, null=True)
    nfactor = models.CharField(max_length=16, null=True)
    dfactor = models.CharField(max_length=16, null=True)
    expression = models.CharField(max_length=256, null=True)
    exact = models.CharField(max_length=3, null=True)
    sf = models.IntegerField(null=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'factors'
        db_table_comment = 'Table of factors'
        app_label = 'units'


class Dimensions(models.Model):
    quantitysystem = models.ForeignKey(Quantitysystems, on_delete=models.PROTECT, db_column='quantitysystem_id')
    name = models.CharField(max_length=128)
    type = models.CharField(max_length=64, null=True)
    symbol = models.CharField(max_length=256, null=True)
    qudtstring = models.CharField(max_length=128, null=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'dimensions'
        db_table_comment = 'Table of dimensions'
        app_label = 'units'


class Entities(models.Model):
    unit = models.ForeignKey('Units', on_delete=models.PROTECT, null=True, db_column='unit_id')
    repsys = models.CharField(max_length=16)
    repsystem = models.ForeignKey(Repsystems, on_delete=models.PROTECT, db_column='repsystem_id', null=True)
    name = models.CharField(max_length=64, null=True)
    lang = models.CharField(max_length=16, null=True)
    symbol = models.CharField(max_length=128, null=True)
    quantity = models.CharField(max_length=1024, null=True)
    quantityid = models.CharField(max_length=1024, null=True)
    value = models.CharField(max_length=128, null=True)
    source = models.CharField(max_length=32, null=True)
    comment = models.CharField(max_length=1024, null=True)
    migrated = models.CharField(max_length=3, null=True)
    lastcheck = models.DateField(null=True)
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
    name = models.CharField(max_length=128)
    url = models.CharField(max_length=128, null=True)
    isq = models.CharField(max_length=128, null=True)
    source = models.CharField(max_length=128, null=True)
    section = models.CharField(max_length=16, null=True)
    quant = models.CharField(max_length=128, null=True)
    quantity = models.ForeignKey(Quantities, on_delete=models.PROTECT, db_column='quantity_id', null=True)
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
    label = models.CharField(max_length=32, null=True)
    silabel = models.CharField(max_length=32, null=True)
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
    name = models.CharField(max_length=64)
    sitype = models.ForeignKey(Wdsiclasses, on_delete=models.PROTECT, db_column='sitype', null=True)
    wdclass = models.ForeignKey(Wdclasses, on_delete=models.PROTECT, db_column='wdclass_id', null=True)
    factor = models.CharField(max_length=256, null=True)
    wdfacunit = models.ForeignKey('self', on_delete=models.PROTECT, db_column='wdfacunit_id', null=True)
    code = models.CharField(max_length=128, null=True)
    checked = models.CharField(max_length=3, choices=Checked, default=Checked.NO)
    added = models.DateField(auto_now_add=True)
    comment = models.CharField(max_length=256, null=True)
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
    quant = models.ForeignKey(Quantities, on_delete=models.PROTECT, db_column='quantity_id', null=True)
    code = models.CharField(max_length=16, null=True)
    name = models.CharField(max_length=128, null=True)
    isq = models.CharField(max_length=32, null=True)
    source = models.CharField(max_length=128, null=True)
    sect = models.CharField(max_length=16, null=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'wdquants'
        verbose_name_plural = "Wikidata Quantities"
        db_table_comment = 'Table of wikidata quantities'
        app_label = 'units'


class Representations(models.Model):
    unit = models.ForeignKey(Units, on_delete=models.PROTECT, db_column='unit_id', null=True)
    wdunit = models.ForeignKey(Wdunits, on_delete=models.PROTECT, db_column='wdunit_id', null=True)
    repsystem = models.ForeignKey(Repsystems, on_delete=models.PROTECT, db_column='repsystem_id', null=True)
    strng = models.ForeignKey(Strngs, on_delete=models.PROTECT, db_column='strng_id', null=True)
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

    @property
    def iecuid(self):
        # Return IEC code to replace string
        if self.repsystem.id == 15:
            return f"{self.strng.string.replace('/', '-').replace('#', '%23')}"
        else:
            return f""

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


class WdclassesWdunits(models.Model):
    wdclass = models.ForeignKey(Wdclasses, on_delete=models.PROTECT, db_column='wdclass_id')
    wdunit = models.ForeignKey(Wdunits, on_delete=models.PROTECT, db_column='wdunit_id')
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'wdclasses_wdunits'
        unique_together = (('wdunit', 'wdclass'),)
        db_table_comment = 'Join table between wikidata classes and units'
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


class Qudtunits(models.Model):
    name = models.CharField(max_length=64, null=True)
    code = models.CharField(max_length=32, null=True)
    dimvector = models.CharField(max_length=128, null=True)
    siexact = models.CharField(max_length=32, null=True)
    replaces = models.CharField(max_length=256, null=True)
    defunitsystems = models.CharField(max_length=128, null=True)
    dercohsystems = models.CharField(max_length=128, null=True)
    derunitsystems = models.CharField(max_length=512, null=True)
    multiplier = models.CharField(max_length=256, null=True)
    omunit = models.CharField(max_length=256, null=True)
    wdunit = models.CharField(max_length=256, null=True)
    ieccodes = models.CharField(max_length=128, null=True)
    ucumcodes = models.CharField(max_length=128, null=True)
    unececodes = models.CharField(max_length=16, null=True)
    symbol = models.CharField(max_length=64, null=True)
    normrefs = models.CharField(max_length=1024, null=True)
    infrefs = models.CharField(max_length=1024, null=True)
    description = models.CharField(max_length=2048, null=True)
    altlabel = models.CharField(max_length=64, null=True)
    dbpedia = models.CharField(max_length=256, null=True)
    latexsymbol = models.CharField(max_length=128, null=True)
    otherreps = models.CharField(max_length=1024, null=True)
    unit = models.ForeignKey(Units, models.DO_NOTHING, db_column='unit_id')
    new = models.CharField(max_length=3, choices=Checked, default=Checked.NO)
    checked = models.CharField(max_length=3, choices=Checked, default=Checked.NO)
    updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'qudtunits'
        db_table_comment = 'Table of QUDT unit entries'
        app_label = 'units'


class Qudtqkinds(models.Model):
    name = models.CharField(max_length=128, null=True)
    code = models.CharField(max_length=128, null=True)
    replaces = models.CharField(max_length=256, null=True)
    units = models.CharField(max_length=512, null=True)
    description = models.TextField(null=True)
    text = models.TextField(null=True)
    dimvector = models.CharField(max_length=64, null=True)
    ddimvector = models.CharField(max_length=64, null=True)
    ndimvector = models.CharField(max_length=64, null=True)
    basecgsdims = models.CharField(max_length=256, null=True)
    baseimpdims = models.CharField(max_length=256, null=True)
    baseisodims = models.CharField(max_length=256, null=True)
    basesidims = models.CharField(max_length=256, null=True)
    baseusdims = models.CharField(max_length=256, null=True)
    altlabels = models.CharField(max_length=512, null=True)
    latexdefn = models.CharField(max_length=1024, null=True)
    latexsymb = models.CharField(max_length=128, null=True)
    symbols = models.CharField(max_length=128, null=True)
    nrefs = models.CharField(max_length=1024, null=True)
    infrefs = models.CharField(max_length=1024, null=True)
    isorefs = models.CharField(max_length=1024, null=True)
    matches = models.CharField(max_length=512, null=True)
    cmatches = models.CharField(max_length=512, null=True)
    ematches = models.CharField(max_length=512, null=True)
    urls = models.CharField(max_length=256, null=True)
    pedia = models.CharField(max_length=256, null=True)
    wdata = models.CharField(max_length=256, null=True)
    iec = models.CharField(max_length=32, null=True)
    broader = models.CharField(max_length=512, null=True)
    sameas = models.CharField(max_length=1024, null=True)
    seealso = models.CharField(max_length=512, null=True)
    comesfrom = models.CharField(max_length=512, null=True)
    abbrevs = models.CharField(max_length=512, null=True)
    comments = models.CharField(max_length=1024, null=True)
    new = models.CharField(max_length=3, choices=Checked, default=Checked.NO)
    checked = models.CharField(max_length=3, choices=Checked, default=Checked.NO)
    updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'qudtqkinds'
        db_table_comment = 'Table of QUDT unit entries'
        app_label = 'units'


class QudtqkindsQudtunits(models.Model):
    qudtqkind = models.ForeignKey(Qudtqkinds, models.DO_NOTHING)
    qudtunit = models.ForeignKey(Qudtunits, models.DO_NOTHING)
    checked = models.CharField(max_length=3, choices=Checked, default=Checked.NO)
    updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'qudtqkinds_qudtunits'
        db_table_comment = 'Join table for qudt units a qkinds'
        app_label = 'units'


class UnitsystemsQudtunits(models.Model):
    unitsystem = models.ForeignKey(Unitsystems, models.DO_NOTHING, null=True)
    qudtunit = models.ForeignKey(Qudtunits, models.DO_NOTHING)
    checked = models.CharField(max_length=3, choices=Checked, default=Checked.NO)
    updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'unitsystems_qudtunits'
        db_table_comment = 'Join table for qudt units a quantity systems'
        app_label = 'units'
