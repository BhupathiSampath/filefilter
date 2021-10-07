from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls import url
# from tsvfile.management.commands.add_data import Command
from split.api.add_data import adddata
from split.api.filtered_data import max_date, LineageFilter, MutationFilter, Filter, Filter1, filter2,exportcsv
urlpatterns = [
    path('adddata/', adddata.as_view(), name='adddata'),
    path('max_date/', max_date.as_view(), name='max_date'),
    path('lineagefilter/', LineageFilter.as_view(), name='lineagefilter'),
    path('mutatiofilter/', MutationFilter.as_view(), name='mutatiofilter'),
    path('filter/', Filter.as_view(), name='filter'),
    path('data/', Filter1.as_view(), name='data'),
    path('data1/', filter2.as_view(), name='data1'),
    path('exportcsv/', exportcsv.as_view(), name='exportcsv'),
]