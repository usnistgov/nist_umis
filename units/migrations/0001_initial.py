# Generated by Django 4.1.5 on 2023-01-12 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Correspondents',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('factor', models.FloatField(blank=True, null=True)),
                ('factoreqn', models.CharField(blank=True, max_length=64, null=True)),
                ('updated', models.DateTimeField()),
            ],
            options={
                'db_table': 'correspondents',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Dimensions',
            fields=[
                ('id', models.SmallAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128)),
                ('type', models.CharField(max_length=64)),
                ('symbol', models.CharField(max_length=256)),
                ('qudtstring', models.CharField(max_length=128)),
                ('updated', models.DateTimeField()),
            ],
            options={
                'db_table': 'dimensions',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Dimensionvectors',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=2048)),
                ('description', models.CharField(max_length=1024)),
                ('dim_exp_l', models.DecimalField(db_column='dim_exp_L', decimal_places=1, max_digits=2)),
                ('dim_exp_m', models.DecimalField(db_column='dim_exp_M', decimal_places=1, max_digits=2)),
                ('dim_exp_t', models.DecimalField(db_column='dim_exp_T', decimal_places=1, max_digits=2)),
                ('dim_exp_i', models.DecimalField(db_column='dim_exp_I', decimal_places=1, max_digits=2)),
                ('dim_exp_h', models.DecimalField(db_column='dim_exp_H', decimal_places=1, max_digits=2)),
                ('dim_exp_n', models.DecimalField(db_column='dim_exp_N', decimal_places=1, max_digits=2)),
                ('dim_exp_j', models.DecimalField(db_column='dim_exp_J', decimal_places=1, max_digits=2)),
                ('dim_exp_d', models.DecimalField(db_column='dim_exp_D', decimal_places=1, max_digits=2)),
                ('shortcode', models.CharField(blank=True, max_length=32, null=True)),
                ('longcode', models.CharField(blank=True, max_length=128, null=True)),
                ('symbol', models.CharField(max_length=512)),
                ('basesi_shortcode', models.CharField(blank=True, max_length=512, null=True)),
                ('basesi_longcode', models.CharField(blank=True, max_length=512, null=True)),
                ('updated', models.DateTimeField()),
            ],
            options={
                'db_table': 'dimensionvectors',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Domains',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64)),
                ('type', models.CharField(max_length=32)),
                ('description', models.CharField(max_length=512)),
                ('updated', models.DateTimeField()),
            ],
            options={
                'verbose_name_plural': 'domains',
                'db_table': 'domains',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Encodings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('string', models.CharField(max_length=512)),
                ('format', models.CharField(max_length=7)),
                ('updated', models.DateTimeField()),
            ],
            options={
                'db_table': 'encodings',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Entities',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('repsys', models.CharField(max_length=16)),
                ('name', models.CharField(blank=True, max_length=64, null=True)),
                ('lang', models.CharField(blank=True, max_length=16, null=True)),
                ('symbol', models.CharField(blank=True, max_length=128, null=True)),
                ('quantity', models.CharField(blank=True, max_length=1024, null=True)),
                ('quantityid', models.CharField(blank=True, max_length=1024, null=True)),
                ('value', models.CharField(blank=True, max_length=128, null=True)),
                ('source', models.CharField(blank=True, max_length=32, null=True)),
                ('comment', models.CharField(blank=True, max_length=1024, null=True)),
                ('lastupdate', models.DateField(blank=True, null=True)),
                ('updated', models.DateTimeField()),
            ],
            options={
                'db_table': 'entities',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Equivalents',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('factor', models.FloatField(blank=True, null=True)),
                ('updated', models.DateTimeField()),
            ],
            options={
                'db_table': 'equivalents',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Factors',
            fields=[
                ('id', models.SmallAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128)),
                ('nfactor', models.CharField(max_length=16)),
                ('dfactor', models.CharField(max_length=16)),
                ('exact', models.CharField(max_length=3)),
                ('sf', models.IntegerField(blank=True, null=True)),
                ('updated', models.DateTimeField()),
            ],
            options={
                'db_table': 'factors',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Prefixes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_collation='utf8_unicode_ci', max_length=32)),
                ('symbol', models.CharField(db_collation='utf8_unicode_ci', max_length=64)),
                ('value', models.CharField(db_collation='utf8_unicode_ci', max_length=32)),
                ('inverse', models.CharField(blank=True, db_collation='utf8_unicode_ci', max_length=32, null=True)),
                ('updated', models.DateTimeField()),
            ],
            options={
                'db_table': 'prefixes',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Quantities',
            fields=[
                ('id', models.SmallAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128)),
                ('altnames', models.CharField(max_length=512)),
                ('description', models.CharField(blank=True, max_length=1024, null=True)),
                ('symbol', models.CharField(blank=True, max_length=128, null=True)),
                ('latexsymbol', models.CharField(blank=True, max_length=512, null=True)),
                ('latexdefn', models.CharField(blank=True, max_length=512, null=True)),
                ('url', models.CharField(blank=True, max_length=256, null=True)),
                ('domain_id', models.IntegerField(blank=True, null=True)),
                ('updated', models.DateTimeField()),
                ('sysml_name', models.CharField(blank=True, max_length=128, null=True)),
                ('sysml_domain', models.CharField(blank=True, max_length=32, null=True)),
                ('sysml_defn', models.CharField(blank=True, max_length=512, null=True)),
                ('sysml_symbol', models.CharField(blank=True, max_length=32, null=True)),
                ('sysml_numtype', models.CharField(blank=True, max_length=128, null=True)),
                ('sysml_unittype', models.CharField(blank=True, max_length=128, null=True)),
                ('sysml_torder', models.IntegerField(blank=True, null=True)),
                ('sysml_qdim', models.CharField(blank=True, max_length=64, null=True)),
                ('sysml_unit', models.CharField(blank=True, max_length=128, null=True)),
                ('sysml_remark', models.CharField(blank=True, max_length=256, null=True)),
                ('iso_source', models.CharField(blank=True, max_length=256, null=True)),
                ('iso_item', models.CharField(blank=True, max_length=8, null=True)),
                ('done', models.CharField(max_length=3)),
            ],
            options={
                'db_table': 'quantities',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Quantitykinds',
            fields=[
                ('id', models.SmallAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128)),
                ('shortname', models.CharField(blank=True, max_length=128, null=True)),
                ('type', models.CharField(blank=True, max_length=16, null=True)),
                ('description', models.CharField(blank=True, max_length=1024, null=True)),
                ('symbol', models.CharField(max_length=64)),
                ('shortcode', models.CharField(blank=True, max_length=128, null=True)),
                ('baseunit_id', models.IntegerField(blank=True, null=True)),
                ('updated', models.DateTimeField()),
            ],
            options={
                'db_table': 'quantitykinds',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='QuantitykindsUnits',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated', models.DateTimeField()),
            ],
            options={
                'db_table': 'quantitykinds_units',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Quantitysystems',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('description', models.CharField(max_length=1024)),
                ('abbrev', models.CharField(max_length=16)),
                ('url', models.CharField(max_length=256)),
                ('updated', models.DateTimeField()),
            ],
            options={
                'db_table': 'quantitysystems',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Representations',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(blank=True, max_length=256, null=True)),
                ('updated', models.DateTimeField()),
            ],
            options={
                'db_table': 'representations',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Repsystems',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('abbrev', models.CharField(blank=True, max_length=16, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('version', models.CharField(blank=True, max_length=32, null=True)),
                ('type', models.CharField(blank=True, max_length=13, null=True)),
                ('status', models.CharField(blank=True, max_length=7, null=True)),
                ('url', models.CharField(blank=True, max_length=256, null=True)),
                ('repository', models.CharField(blank=True, max_length=256, null=True)),
                ('fileupdated', models.DateField()),
                ('fileformat', models.CharField(blank=True, max_length=8, null=True)),
                ('checked', models.DateTimeField()),
                ('jsondata', models.TextField(blank=True, null=True)),
                ('updated', models.DateTimeField()),
            ],
            options={
                'verbose_name_plural': 'repsystems',
                'db_table': 'repsystems',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Strngs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('string', models.CharField(max_length=512)),
                ('status', models.CharField(blank=True, max_length=11, null=True)),
                ('reason', models.CharField(blank=True, max_length=128, null=True)),
                ('updated', models.DateTimeField()),
            ],
            options={
                'db_table': 'strngs',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Units',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('description', models.CharField(blank=True, max_length=1024, null=True)),
                ('prefix_id', models.IntegerField(blank=True, null=True)),
                ('factor_id', models.SmallIntegerField(blank=True, null=True)),
                ('url', models.CharField(blank=True, max_length=256, null=True)),
                ('type', models.CharField(blank=True, max_length=19, null=True)),
                ('shortcode', models.CharField(blank=True, max_length=512, null=True)),
                ('alt_shortcode', models.CharField(blank=True, max_length=512, null=True)),
                ('ivoa', models.CharField(blank=True, max_length=512, null=True)),
                ('html', models.CharField(blank=True, max_length=256, null=True)),
                ('text', models.CharField(blank=True, max_length=128, null=True)),
                ('text_si', models.CharField(blank=True, db_column='text_SI', max_length=128, null=True)),
                ('updated', models.DateTimeField()),
            ],
            options={
                'verbose_name_plural': 'units',
                'db_table': 'units',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Unitsystems',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('description', models.CharField(max_length=1024)),
                ('abbrev', models.CharField(max_length=16)),
                ('url', models.CharField(max_length=256)),
                ('updated', models.DateTimeField()),
            ],
            options={
                'db_table': 'unitsystems',
                'managed': False,
            },
        ),
    ]
