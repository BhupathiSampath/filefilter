from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls import url
# from tsvfile.management.commands.add_data import Command
from split.api.add_data import adddata
from split.api.filtered_data import max_date, Filter, filter2,exportcsv,uniqeseq, uniqelineage, Pangovarsionlist
urlpatterns = [
    path('adddata/', adddata.as_view(), name='adddata'),
    path('max_date/', max_date.as_view(), name='max_date'),
    path('filter/', Filter.as_view(), name='filter'),
    path('data1/', filter2.as_view(), name='data1'),
    path('exportcsv/', exportcsv.as_view(), name='exportcsv'),
    path('count/', uniqeseq.as_view(), name='count'),
    path('lineagedrop/', uniqelineage.as_view(), name='lineagedrop'),
    path('pangoversion/', Pangovarsionlist.as_view(), name='pangoversion'),
]