from itertools import groupby
from rest_framework import status
import pandas as pd
from pyexpat import model
from split.models import tsvfile
from django.db.models import Count
from datetime import date, timedelta
from rest_framework import pagination
from rest_framework import serializers
from django.db.models.query_utils import Q
from rest_framework.response import Response
from split.api.filtered_data import LocationFilter
from django.db.models.expressions import Subquery, Value
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView, RetrieveAPIView
from django_filters.rest_framework.backends import DjangoFilterBackend


class LineageClassificationSerializer(serializers.ModelSerializer):
    strain__count = serializers.IntegerField(read_only=True,)

    class Meta:
        model = tsvfile
        fields = ('Class', 'strain__count')


class LineageClassificationDistribution(ListAPIView):
    serializer_class = LineageClassificationSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = LocationFilter

    filter_fields = ('index', 'date', 'start_date', 'end_date', 'strain', 'reference_id',
                     'mutation', 'amino_acid_position', 'gene', 'mutation_deletion',)
    search_fields = ('index', 'date', 'strain', 'state', 'lineage', 'reference_id',
                     'mutation', 'amino_acid_position', 'gene', 'mutation_deletion',)
    ordering_fields = ['index', 'date', 'strain', 'state', 'lineage', 'reference_id',
                       'mutation', 'amino_acid_position', 'gene', 'mutation_deletion', ]

    def get_queryset(self):
        days = int(self.request.GET.get('days', 3650))
        year = self.request.GET.get('year', "2021,2022")
        days = date.today()-timedelta(days=days)
        QuerySet = tsvfile.objects.filter(date__gte=days, year__in=year.split(',')).order_by(
        ).values('Class').annotate(Count('strain', distinct=True))
        return QuerySet


class MonthlyClassificationSerializer(serializers.ModelSerializer):
    strain__count = serializers.IntegerField(read_only=True,)

    class Meta:
        model = tsvfile
        fields = ("month_number", "Class", "strain__count",)


class MonthlyClassificationStackBar(ListAPIView):
    serializer_class = MonthlyClassificationSerializer
    # pagination_class = LargeResultsSetPagination
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_class = LocationFilter
    filter_fields = ('index', 'date', 'start_date', 'end_date', 'strain', 'state', 'lineage',
                     'reference_id', 'mutation', 'amino_acid_position', 'gene', 'mutation_deletion',)
    search_fields = ('index', 'date', 'strain', 'state', 'lineage', 'reference_id',
                     'mutation', 'amino_acid_position', 'gene', 'mutation_deletion',)
    ordering_fields = ['index', 'date', 'strain', 'state', 'lineage', 'reference_id',
                       'mutation', 'amino_acid_position', 'gene', 'mutation_deletion', ]

    def get(self, request):
        days = int(self.request.GET.get('days', 3650))
        year = self.request.GET.get('year', "202")
        days = date.today()-timedelta(days=days)
        QuerySet = tsvfile.objects.filter(date__gte=days, month_number__icontains=year).values(
            'month_number', 'Class').annotate(Count('strain', distinct=True)).order_by('date__year', 'date__month')
        mnd = {}
        mnlist = []
        for dic in QuerySet:
            v = dic['month_number']
            if v not in mnlist:
                mnlist.append(v)
        mnd['month_number'] = mnlist
        df = pd.DataFrame(QuerySet)
        df = df.set_index('month_number')
        dfT = df.T
        req_list = []
        for j in list(dfT.loc['Class'].unique()):
            t = {}
            t['Class'] = j
            t['value'] = []
            req_list.append(t)
        df2 = pd.DataFrame(QuerySet)
        df2 = df2.set_index(['month_number', 'Class'])
        for dic in req_list:
            lndic = dic['Class']
            months = mnd['month_number']
            for month in months:
                if lndic in df2.loc[month].index:
                    val = df2.loc[month, lndic]['strain__count']
                    dic['value'].append(val)
                else:
                    dic['value'].append(0)
        return Response({"month": mnd, "lineage": req_list})


class WeeklyClassificationSerializer(serializers.ModelSerializer):
    strain__count = serializers.IntegerField(read_only=True,)

    class Meta:
        model = tsvfile
        fields = ("week_number", "Class", "strain__count",)


class WeeklyClassificationStackBar(ListAPIView):
    serializer_class = WeeklyClassificationSerializer
    # pagination_class = LargeResultsSetPagination
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_class = LocationFilter
    filter_fields = ('index', 'date', 'start_date', 'end_date', 'strain', 'state', 'lineage',
                     'reference_id', 'mutation', 'amino_acid_position', 'gene', 'mutation_deletion',)
    search_fields = ('index', 'date', 'strain', 'state', 'lineage', 'reference_id',
                     'mutation', 'amino_acid_position', 'gene', 'mutation_deletion',)
    ordering_fields = ['index', 'date', 'strain', 'state', 'lineage', 'reference_id',
                       'mutation', 'amino_acid_position', 'gene', 'mutation_deletion', ]

    def get(self, request):
        days = int(self.request.GET.get('days', 3650))
        year = self.request.GET.get('year', "202")
        days = date.today()-timedelta(days=days)
        QuerySet = tsvfile.objects.filter(date__gte=days, month_number__icontains=year).values(
            'week_number', 'Class').annotate(Count('strain', distinct=True))
        mnd = {}
        mnlist = []
        for dic in QuerySet:
            v = dic['week_number']
            if v not in mnlist:
                mnlist.append(v)
        mnd['week_number'] = mnlist
        df = pd.DataFrame(QuerySet)
        df = df.set_index('week_number')
        dfT = df.T
        req_list = []
        for j in list(dfT.loc['Class'].unique()):
            t = {}
            t['Class'] = j
            t['value'] = []
            req_list.append(t)
        df2 = pd.DataFrame(QuerySet)
        df2 = df2.set_index(['week_number', 'Class'])
        for dic in req_list:
            lndic = dic['Class']
            months = mnd['week_number']
            for month in months:
                if lndic in df2.loc[month].index:
                    val = df2.loc[month, lndic]['strain__count']
                    dic['value'].append(val)
                else:
                    dic['value'].append(0)
        return Response({"month": mnd, "lineage": req_list})
