# Generated by Django 3.2.7 on 2021-11-05 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('split', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tsvfile',
            name='amino_acid_position',
            field=models.IntegerField(blank=True, default=None, max_length=225, null=True),
        ),
    ]