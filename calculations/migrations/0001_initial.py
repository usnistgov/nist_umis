# Generated by Django 4.1.3 on 2022-11-29 19:43

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Calculations',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request', models.CharField(max_length=128)),
                ('data', models.CharField(max_length=1024)),
                ('comments', models.CharField(max_length=256)),
                ('updated', models.DateTimeField()),
            ],
            options={
                'db_table': 'calculations',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Equations',
            fields=[
                ('id', models.SmallAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('description', models.CharField(max_length=128)),
                ('mathjson', models.CharField(max_length=1024)),
                ('comments', models.CharField(max_length=256)),
                ('updated', models.DateTimeField()),
            ],
            options={
                'db_table': 'equations',
                'managed': False,
            },
        ),
    ]