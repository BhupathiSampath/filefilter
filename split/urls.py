from split.api.monthly_lineages import MonthlyLineageStackBar, MonthlyDistribution
from split.api.filterfunction import (LineageClassificationWeekly,
                                      WeeklyLineageStackBar, StatesLineageClassification, LineageClassificationMonth)
from split.api.lineage_analysis import StatesMutationDistribution, Frequency, StatesLineageDistribution, StatesSequenceDistribution, StackBar, StackBar2, GenomesSeqenced, IncreaseInStrain
from split.api.Classification import LineageClassificationDistribution, MonthlyClassificationStackBar, WeeklyClassificationStackBar
from django.conf.urls import url
from django.contrib import admin
from split.api.add_data import adddata
from django.urls import path, include, re_path
# from tsvfile.management.commands.add_data import Command
from split.api.uniquelineagestrain import UniqueLineageStrain, UniqeLineageCount
from split.api.filtered_data import max_date, Filter, exportcsv, uniqeseq, Pangovarsionlist, AdvanceFiltering, Distribution, googlChart, D3Chart
# from split.api.filetrbackend import RestView
urlpatterns = [
    # path('login/', UserLoginView.as_view(), name='login'),
    # Upload data
    path('adddata/', adddata.as_view(), name='adddata'),

    # Fetch data APIs
    path('max_date/', max_date.as_view(), name='max_date'),
    path('data/', Filter.as_view(), name='filter'),
    path('exportcsv/', exportcsv.as_view(), name='exportcsv'),
    path('count/', uniqeseq.as_view(), name='count'),
    path('pangoversion/', Pangovarsionlist.as_view(), name='pangoversion'),
    path('advanceddata/', AdvanceFiltering.as_view(), name='advanceddata'),
    path('frequency/', Frequency.as_view(), name='frequency'),
    path('statesmutationdistribution/', StatesMutationDistribution.as_view(),
         name='statesmutationdistribution'),
    path('stateslineagedistribution/', StatesLineageDistribution.as_view(),
         name='stateslineagedistribution'),
    path('distribution/', Distribution.as_view(), name='distribution'),
    path('googlchart/', googlChart.as_view(), name='googlchart'),
    path('d3chart/', D3Chart.as_view(), name='d3chart'),

    path('monthlydistribution/', MonthlyDistribution.as_view(),
         name='monthlydistribution'),
    path('statesequencesdistribution/', StatesSequenceDistribution.as_view(),
         name='statesequencesdistribution'),
    path('stackbar/', StackBar.as_view(), name='stackbar'),
    path('stackbar2/', StackBar2.as_view(), name='stackbar2'),
    path('weeklylineages/', WeeklyLineageStackBar.as_view(), name='weeklystackbar'),
    path('monthlylineages/', MonthlyLineageStackBar.as_view(),
         name='monthlylineages'),


    path('genomesseqenced/', GenomesSeqenced.as_view(), name='genomesseqenced'),
    path('uniqelineagecount/', UniqeLineageCount.as_view(),
         name='uniqelineagecount'),
    path('uniquelineagestrain/', UniqueLineageStrain.as_view(),
         name='uniquelineagestrain'),
    path('increaseinstrain/', IncreaseInStrain.as_view(), name='increaseinstrain'),

    # Classification APIs
    path('linclassification/', LineageClassificationDistribution.as_view(),
         name='linclassification'),
    path('monthlylinclassification/', MonthlyClassificationStackBar.as_view(),
         name='monthlylinclassification'),
    path('weeklylinclassification/', WeeklyClassificationStackBar.as_view(),
         name='weeklylinclassification'),


    path('lineageclassificationmonth/', LineageClassificationMonth.as_view(),
         name='lineageclassificationmonth'),
    path('lineageclassificationweekly/', LineageClassificationWeekly.as_view(),
         name='lineageclassificationweekly'),
    path('stateslineageclassification/', StatesLineageClassification.as_view(),
         name='stateslineageclassification'),
]
