# Generated by Django 3.2.7 on 2021-10-04 06:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('split', '0004_tsvfile_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tsvfile',
            name='date',
            field=models.DateField(verbose_name='03/16/2020 04:31 PM'),
        ),
    ]
