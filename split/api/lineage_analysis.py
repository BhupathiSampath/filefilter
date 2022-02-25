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

class LargeResultsSetPagination(PageNumberPagination):  
    page_size = 100
    page_size_query_param = 'page_size'


class MutationDistributionSerializer(serializers.ModelSerializer):
    mutation_deletion__count = serializers.IntegerField(read_only=True,)
    class Meta:
        model = tsvfile
        fields = ("state", "mutation_deletion__count",)


class StatesMutationDistribution(ListAPIView):
    serializer_class = MutationDistributionSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = LocationFilter
    
    filter_fields = ('index', 'date', 'start_date', 'end_date', 'strain', 'reference_id','mutation','amino_acid_position','gene','mutation_deletion',)
    def get_queryset(self):
        QuerySet = tsvfile.objects.values('state').annotate(Count('mutation_deletion', distinct=True))
        # df = pd.DataFrame(list(tsvfile.objects.values("state", "mutation_deletion")))
        # df = df['mutation_deletion'].groupby(df['state']).nunique().reset_index(name="count")
        # # df = pd.DataFrame(df)
        # QuerySet = df.to_dict("series")
        return QuerySet
        # return Response({"data": QuerySet})
        
class StateDistributionSerializer(serializers.ModelSerializer):
    strain__count = serializers.IntegerField(read_only=True,)
    class Meta:
        model = tsvfile
        fields = ("state","strain__count",)

class StatesSequenceDistribution(ListAPIView):
    serializer_class = StateDistributionSerializer
    filter_backends = (DjangoFilterBackend,SearchFilter,OrderingFilter)
    filter_class = LocationFilter
    filter_fields = ('index','date','start_date','end_date','strain','state','lineage','reference_id','mutation','amino_acid_position','gene','mutation_deletion',)
    search_fields = ('index','date','strain','state','lineage','reference_id','mutation','amino_acid_position','gene','mutation_deletion',)
    ordering_fields = ['index','date','strain','state','lineage','reference_id','mutation','amino_acid_position','gene','mutation_deletion',]
    def get_queryset(self):
        days = int(self.request.GET.get('days',3650))
        year = self.request.GET.get('year',"202")
        days=date.today()-timedelta(days=days)
        QuerySet = tsvfile.objects.filter(date__gte=days,month_number__icontains=year).values('state').annotate(Count('strain', distinct=True))
        return QuerySet

class LineageDistributionSerializer(serializers.ModelSerializer):
    lineage__count = serializers.IntegerField(read_only=True,)
    class Meta:
        model = tsvfile
        fields = ("state","lineage__count",)

class StatesLineageDistribution(RetrieveAPIView):
    serializer_class = LineageDistributionSerializer
    def get_queryset(self):
        QuerySet = tsvfile.objects.values('state').annotate(Count('lineage', distinct=True))
        return QuerySet



class Frequency(RetrieveAPIView):
    pagination_class = LargeResultsSetPagination
    def get(self, request):
        df = pd.DataFrame(list(tsvfile.objects.all().values()))
        df = df.groupby(["state", 'lineage', "mutation_deletion"]).size().reset_index(name="count")
        df = pd.DataFrame(df)
        QuerySet = df.to_dict("r")
        return Response({"data": QuerySet})


class MonthDistributionSerializer(serializers.ModelSerializer):
    strain__count = serializers.IntegerField(read_only=True,)
    class Meta:
        model = tsvfile
        fields = ("month_number","strain__count",)

import datetime as dt
class MonthlyDistribution(ListAPIView):
    serializer_class = MonthDistributionSerializer
    filter_backends = (DjangoFilterBackend,SearchFilter,OrderingFilter)
    filter_class = LocationFilter
    filter_fields = ('index','date','start_date','end_date','strain','state','lineage','reference_id','mutation','amino_acid_position','gene','mutation_deletion',)
    search_fields = ('index','date','strain','state','lineage','reference_id','mutation','amino_acid_position','gene','mutation_deletion',)
    ordering_fields = ['index','date','strain','state','lineage','reference_id','mutation','amino_acid_position','gene','mutation_deletion',]
    def get_queryset(self):
        days = int(self.request.GET.get('days',3650))
        year = self.request.GET.get('year',"202")
        days=date.today()-timedelta(days=days)
        QuerySet = tsvfile.objects.filter(date__gte=days,month_number__icontains=year).values('month_number',).annotate(Count('strain', distinct=True)).order_by('date__year','date__month')
        return QuerySet




class WeeklyLineageSerializer(serializers.ModelSerializer):
    strain__count = serializers.IntegerField(read_only=True,)
    class Meta:
        model = tsvfile
        fields = ("week_number","lineage","strain__count",)

from itertools import groupby
class WeeklyLineageStackBar(ListAPIView):
    serializer_class = WeeklyLineageSerializer
    # pagination_class = LargeResultsSetPagination
    filter_backends = (DjangoFilterBackend,SearchFilter,OrderingFilter)
    filter_class = LocationFilter
    filter_fields = ('index','date','start_date','end_date','strain','state','lineage','reference_id','mutation','amino_acid_position','gene','mutation_deletion',)
    search_fields = ('index','date','strain','state','lineage','reference_id','mutation','amino_acid_position','gene','mutation_deletion',)
    ordering_fields = ['index','date','strain','state','lineage','reference_id','mutation','amino_acid_position','gene','mutation_deletion',]
    def get(self, request):
        days = int(self.request.GET.get('days',3650))
        year = self.request.GET.get('year',"202")
        days=date.today()-timedelta(days=days)
        QuerySet = tsvfile.objects.filter(date__gte=days,month_number__icontains=year, lineage__in=["AY.1","BA.1"]).values('week_number','lineage').annotate(Count('strain', distinct=True))
        mnd = {} ; mnlist = [] 
        for dic in QuerySet:
            v = dic['week_number']
            if v not in mnlist:
                mnlist.append(v)
        mnd['week_number'] = mnlist
        df = pd.DataFrame(QuerySet);df = df.set_index('week_number');
        dfT = df.T ;
        req_list = []
        for j in list(dfT.loc['lineage'].unique()) :
            t = {} ;
            t['lineage'] = j
            t['value'] = []
            req_list.append(t)
        df2 = pd.DataFrame(QuerySet);
        df2 = df2.set_index(['week_number','lineage']);
        for dic in req_list:
            lndic = dic['lineage']
            months = mnd['week_number']
            for month in months:
                if lndic in df2.loc[month].index:
                    val = df2.loc[month,lndic]['strain__count']
                    dic['value'].append(val)
                else :
                    dic['value'].append(0)
        return Response({"week": mnd, "lineage": req_list})

class StackBarSerializer(serializers.ModelSerializer):
    strain__count = serializers.IntegerField(read_only=True,)
    class Meta:
        model = tsvfile
        fields = ("month_number","lineage","strain__count",)

from itertools import groupby
from rest_framework import status
class StackBar1(ListAPIView):
    serializer_class = StackBarSerializer
    # pagination_class = LargeResultsSetPagination
    filter_backends = (DjangoFilterBackend,SearchFilter,OrderingFilter)
    filter_class = LocationFilter
    filter_fields = ('index','date','start_date','end_date','strain','state','lineage','reference_id','mutation','amino_acid_position','gene','mutation_deletion',)
    search_fields = ('index','date','strain','state','lineage','reference_id','mutation','amino_acid_position','gene','mutation_deletion',)
    ordering_fields = ['index','date','strain','state','lineage','reference_id','mutation','amino_acid_position','gene','mutation_deletion',]
    def get(self, request):
        days = int(self.request.GET.get('days',3650))
        year = self.request.GET.get('year',"202")
        days=date.today()-timedelta(days=days)
        QuerySet = tsvfile.objects.filter(date__gte=days,month_number__icontains=year).values('month_number','lineage').annotate(Count('strain', distinct=True)).order_by('date__year','date__month')
        a = {}
        for k,v in groupby(QuerySet,key=lambda x:x['month_number']):
            a[k]=list(v)
        

        # mn = {} ;
        # for dic in QuerySet:
        #     if dic['month_number'] not in mn.keys():
        #         #mn[dic['mn']] = []
        #         y = [] ;
        #         for k,v in dic.items():
        #             if k != 'month_number':
        #                 y.append((v))
                    
        #             mn[dic['month_number']] = y
        #     else :
        #         j = [] ;
        #         for k,v in dic.items():
        #             if k != 'month_number':
        #                 j.append((v))
                
        #         mn[dic['month_number']].extend(j)
        # nl = [] ;
        # for k,v in mn.items():
        #     ndic = {} ; 
        #     l = len(v) ;
        #     i = 0 ;
        #     if l == 2 :
        #         ndic['month_number'] = k ;
        #         ndic[v[0]] = v[1] ;
        #         nl.append(ndic)
        #         ndic = {} ; 
        #     else :
        #         ndic['month_number'] = k ;
        #         while i < int(l) :
        #             ndic[v[i]] = v[i+1] ;
        #             i += 2
        #         nl.append(ndic)
        # nl
        return Response(a)
        # return QuerySet
class StackBar(ListAPIView):
    serializer_class = StackBarSerializer
    # pagination_class = LargeResultsSetPagination
    filter_backends = (DjangoFilterBackend,SearchFilter,OrderingFilter)
    filter_class = LocationFilter
    filter_fields = ('index','date','start_date','end_date','strain','state','lineage','reference_id','mutation','amino_acid_position','gene','mutation_deletion',)
    search_fields = ('index','date','strain','state','lineage','reference_id','mutation','amino_acid_position','gene','mutation_deletion',)
    ordering_fields = ['index','date','strain','state','lineage','reference_id','mutation','amino_acid_position','gene','mutation_deletion',]
    def get_queryset(self):
        days = int(self.request.GET.get('days',3650))
        year = self.request.GET.get('year',"202")
        days=date.today()-timedelta(days=days)
        # QuerySet1 = tsvfile.objects.filter(date__gte=days,month_number__icontains=year).order_by().values('month_number').distinct()
        QuerySet = tsvfile.objects.filter(date__gte=days,month_number__icontains=year).values('month_number','lineage').annotate(Count('strain', distinct=True))
        return Response(QuerySet)

class StackBar2(ListAPIView):
    serializer_class = StackBarSerializer
    # pagination_class = LargeResultsSetPagination
    filter_backends = (DjangoFilterBackend,SearchFilter,OrderingFilter)
    filter_class = LocationFilter
    filter_fields = ('index','date','start_date','end_date','strain','state','lineage','reference_id','mutation','amino_acid_position','gene','mutation_deletion',)
    search_fields = ('index','date','strain','state','lineage','reference_id','mutation','amino_acid_position','gene','mutation_deletion',)
    ordering_fields = ['index','date','strain','state','lineage','reference_id','mutation','amino_acid_position','gene','mutation_deletion',]
    def get(self, request):
        days = int(self.request.GET.get('days',3650))
        year = self.request.GET.get('year',"202")
        days=date.today()-timedelta(days=days)
        # QuerySet1 = tsvfile.objects.filter(date__gte=days,month_number__icontains=year).order_by().values('month_number').distinct()
        QuerySet = tsvfile.objects.filter(date__gte=days,month_number__icontains=year).values('month_number','lineage').annotate(Count('strain', distinct=True)).order_by('date__year','date__month')
        mnd = {} ; mnlist = [] 
        for dic in QuerySet:
            v = dic['month_number']
            if v not in mnlist:
                mnlist.append(v)
        mnd['month_number'] = mnlist
        df = pd.DataFrame(QuerySet);df = df.set_index('month_number');
        dfT = df.T ;
        req_list = []
        for j in list(dfT.loc['lineage'].unique()) :
            t = {} ;
            t['lineage'] = j
            t['value'] = []
            req_list.append(t)
        df2 = pd.DataFrame(QuerySet);
        df2 = df2.set_index(['month_number','lineage']);
        for dic in req_list:
            lndic = dic['lineage']
            months = mnd['month_number']
            for month in months:
                if lndic in df2.loc[month].index:
                    val = df2.loc[month,lndic]['strain__count']
                    dic['value'].append(val)
                else :
                    dic['value'].append(0)
        return Response({"month": mnd, "lineage": req_list})


class Geneserializer(serializers.ModelSerializer):
    class Meta:
        model = tsvfile
        fields = ("strain",)
class GenomesSeqenced(ListAPIView):
    serializer_class = Geneserializer
    pagination_class = LargeResultsSetPagination
    filter_backends = (DjangoFilterBackend,SearchFilter,OrderingFilter)
    filterset_class = LocationFilter
    
    filter_fields = ('index','date','start_date','end_date','strain','reference_id','mutation','amino_acid_position','gene','mutation_deletion',)
    search_fields = ('index','date','strain','state','lineage','reference_id','mutation','amino_acid_position','gene','mutation_deletion',)
    ordering_fields = ['index','date','strain','state','lineage','reference_id','mutation','amino_acid_position','gene','mutation_deletion',]
    def get_queryset(self):
        # QuerySet = tsvfile.objects.all().annotate(Count('strain'))
        QuerySet = tsvfile.objects.order_by().values('strain').distinct()
        return QuerySet

class IncreaseInStrainSerializer(serializers.ModelSerializer):
    strain__count = serializers.IntegerField(read_only=True,)
    class Meta:
        model = tsvfile
        fields = ("state", "strain__count")

class IncreaseInStrain(ListAPIView):
    serializer_class = IncreaseInStrainSerializer
    pagination_class = LargeResultsSetPagination
    filter_backends = (DjangoFilterBackend,SearchFilter,OrderingFilter)
    filter_class = LocationFilter
    filter_fields = ('index','date','start_date','end_date','strain','state','lineage','reference_id','mutation','amino_acid_position','gene','mutation_deletion',)
    search_fields = ('index','date','strain','state','lineage','reference_id','mutation','amino_acid_position','gene','mutation_deletion',)
    ordering_fields = ['index','date','strain','state','lineage','reference_id','mutation','amino_acid_position','gene','mutation_deletion',]
    def get_queryset(self):
        days = int(self.request.GET.get('days',3650))
        year = self.request.GET.get('year',"202")
        days=date.today()-timedelta(days=days)
        QuerySet = tsvfile.objects.filter(date__gte=days,month_number__icontains=year).values('state').annotate(Count('strain', distinct=True))
        return QuerySet