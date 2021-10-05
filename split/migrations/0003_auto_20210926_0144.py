# Generated by Django 3.2.7 on 2021-09-25 20:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('split', '0002_auto_20210926_0140'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tsvfile',
            name='amine_acid_position',
            field=models.CharField(blank=True, default=None, max_length=225, null=True),
        ),
        migrations.AlterField(
            model_name='tsvfile',
            name='gene',
            field=models.CharField(blank=True, default=None, max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='tsvfile',
            name='lineage',
            field=models.CharField(blank=True, default=None, max_length=225, null=True),
        ),
        migrations.AlterField(
            model_name='tsvfile',
            name='mutation',
            field=models.CharField(blank=True, default=None, max_length=225, null=True),
        ),
        migrations.AlterField(
            model_name='tsvfile',
            name='reference_id',
            field=models.CharField(blank=True, default=None, max_length=225, null=True),
        ),
        migrations.AlterField(
            model_name='tsvfile',
            name='strain',
            field=models.CharField(blank=True, default=None, max_length=300, null=True),
        ),
    ]
