from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls import url
# from tsvfile.management.commands.add_data import Command
from split.api.add_data import adddata
from split.api.filtered_data import max_date, Filter,exportcsv,uniqeseq, uniqelineage, Pangovarsionlist, AdvanceFiltering, StateData, Distribution
from split.api.lineage_analysis import StatesMutationDistribution, Frequency, StatesLineageDistribution
# from split.api.login import UserLoginView
# from split.api.filetrbackend import RestView
urlpatterns = [
    # path('login/', UserLoginView.as_view(), name='login'),
    path('adddata/', adddata.as_view(), name='adddata'),
    path('max_date/', max_date.as_view(), name='max_date'),
    path('data/', Filter.as_view(), name='filter'),
    path('exportcsv/', exportcsv.as_view(), name='exportcsv'),
    path('count/', uniqeseq.as_view(), name='count'),
    path('lineagedrop/', uniqelineage.as_view(), name='lineagedrop'),
    path('pangoversion/', Pangovarsionlist.as_view(), name='pangoversion'),
    path('advanceddata/', AdvanceFiltering.as_view(), name='advanceddata'),
    path('statedata/', StateData.as_view(), name='statedata'),
    path('frequency/', Frequency.as_view(), name='frequency'),
    path('statesmutationdistribution/', StatesMutationDistribution.as_view(), name='statesmutationdistribution'),
    path('stateslineagedistribution/', StatesLineageDistribution.as_view(), name='stateslineagedistribution'),
    path('distribution/', Distribution.as_view(), name='distribution'),
]