from django.db import models
import datetime, time
import random


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
    
    strain                      = models.CharField(max_length=300,default=None, blank=True, null=True)
    lineage                     = models.CharField(max_length=225,default=None, blank=True, null=True)
    gene                        = models.CharField(max_length=300,default=None, blank=True, null=True)
    reference_id                = models.CharField(max_length=225,default=None, blank=True, null=True)
    amine_acid_position         = models.CharField(max_length=225,default=None, blank=True, null=True)
    mutation                    = models.CharField(max_length=225,default=None, blank=True, null=True)
    date                        = models.DateField(default=None, blank=True,null=True)
    def __str__(self):
        return self.strain