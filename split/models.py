import time
import random
import datetime
from django.db import models


# def str_time_prop(start, end, time_format, prop):
#     """Get a time at a proportion of a range of two formatted times.

#     start and end should be strings specifying times formatted in the
#     given format (strftime-style), giving an interval [start, end].
#     prop specifies how a proportion of the interval to be taken after
#     start.  The returned time will be in the specified format.
#     """

#     stime = time.mktime(time.strptime(start, time_format))
#     etime = time.mktime(time.strptime(end, time_format))

#     ptime = stime + prop * (etime - stime)

# return time.strftime(time_format, time.localtime(ptime))


def random_date(start, end, prop):
    return (start, end, '%m/%d/%Y %I:%M %p', prop)


class tsvfile(models.Model):
    index = models.BigIntegerField(primary_key=True)
    strain = models.CharField(
        max_length=300, default=None, blank=True, null=True)
    lineage = models.CharField(
        max_length=225, default=None, blank=True, null=True)
    gene = models.CharField(
        max_length=300, default=None, blank=True, null=True)
    reference_id = models.CharField(
        max_length=225, default=None, blank=True, null=True)
    amino_acid_position = models.IntegerField(
        default=None, blank=True, null=True)
    mutation = models.CharField(
        max_length=225, default=None, blank=True, null=True)
    date = models.DateField(default=None, blank=True, null=True)
    state = models.CharField(
        max_length=300, default=None, blank=True, null=True)
    mutation_deletion = models.CharField(
        max_length=300, default=None, blank=True, null=True)
    week_number = models.CharField(
        max_length=50, default=None, blank=True, null=True)
    month_number = models.CharField(
        max_length=50, default=None, blank=True, null=True)
    year = models.CharField(
        max_length=50, default=None, blank=True, null=True)
    Class = models.CharField(
        max_length=100, default=None, blank=True, null=True)

    def __str__(self):
        return self.strain


class PangoVarsion(models.Model):
    # index = models.BigIntegerField(primary_key=True)
    version = models.CharField(
        max_length=300, default=None, blank=True, null=True)
    pangolin_version = models.CharField(
        max_length=225, default=None, blank=True, null=True)
    pangoLEARN_version = models.CharField(
        max_length=300, default=None, blank=True, null=True)
    pango_version = models.CharField(
        max_length=225, default=None, blank=True, null=True)
    date = models.DateTimeField(verbose_name="date", auto_now_add=True)

    def __str__(self):
        return self.version
