from django.db.models.query import QuerySet
from django.http import request
import pandas as pd
from django.db.models import fields
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django_filters.rest_framework import DjangoFilterBackend
from pandas.core.frame import DataFrame
from rest_framework import generics, pagination, serializers
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from split.models import tsvfile, PangoVarsion
# import sqlalchemy
from sqlalchemy import create_engine
# from split.api.filetrbackend import DjangoFilterBackend
import csv
import datetime
from datetime import date, timedelta
import pandas as pd
from collections import OrderedDict, namedtuple
import os, re
from django.db.models import Max
from splitting.settings import BASE_DIR
file_name = str(datetime.datetime.today())
new_file = re.sub('[ ;:]', '_', file_name)
path = f'{BASE_DIR}/downloads/tsvfile{new_file}.csv'
f_name = f'tsvfile{new_file}.csv'
class LargeResultsSetPagination(PageNumberPagination):  
    page_size = 100
    page_size_query_param = 'page_size'
class Filterpage(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    # paginated_by = 100
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('path', f_name)
        ]))

from django_filters import Filter, FilterSet

from django_filters.constants import EMPTY_VALUES
import django_filters
from datetime import date, timedelta
from django_filters import rest_framework as filters

class ListFilter(filters.Filter):
    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs
        value_list = value.split(",")
        qs = super().filter(qs, value_list)
        return qs

        
class LocationFilter(filters.FilterSet):
    # d = date.today()-timedelta(days=7)
    index = filters.NumberFilter(lookup_expr='icontains')
    state = filters.CharFilter(lookup_expr='icontains')
    mutation_deletion = filters.CharFilter(lookup_expr='icontains')
    strain = filters.CharFilter(lookup_expr='icontains')
    lineage = ListFilter(field_name="lineage",lookup_expr='in')
    reference_id = filters.CharFilter(lookup_expr='icontains')
    mutation = filters.CharFilter(lookup_expr='icontains')
    amino_acid_position = filters.CharFilter(lookup_expr='icontains')
    gene = filters.CharFilter(lookup_expr='icontains')
    date = filters.CharFilter(lookup_expr='icontains')
    start_date = filters.DateFilter(field_name="date",lookup_expr="gte")
    end_date = filters.DateFilter(field_name="date",lookup_expr="lte")
    # past_data = filters(date__=d)
    # d=date.today()-timedelta(days=7)
    class Meta:
        model = tsvfile
        fields = ['index','date','start_date','end_date','strain','state','lineage','reference_id','mutation','amino_acid_position','gene','mutation_deletion',]



class dataserializer(serializers.ModelSerializer):
    class Meta:
        model = tsvfile
        fields = ('index','date','strain','state','lineage','reference_id','mutation','amino_acid_position','gene','mutation_deletion',)


class dateserializer(serializers.ModelSerializer):
    class Meta:
        model = tsvfile
        fields = ('index','date')
class max_date(RetrieveAPIView):
    serializer_class = dateserializer
    def get(self, request):
        A = tsvfile.objects.order_by('date').first()
        serializer = dateserializer(A, many=True)
        return Response({"data": serializer.data})


class FilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = tsvfile
        fields = "__all__"

class FilterSerializer1(serializers.ModelSerializer):
    days = serializers.IntegerField(required=False)
    class Meta:
        model = tsvfile
        fields = "__all__"

from dateutil.relativedelta import *    
class Filter(ListAPIView):
    serializer_class = dataserializer
    pagination_class = LargeResultsSetPagination
    filter_backends = (DjangoFilterBackend,SearchFilter,OrderingFilter)
    filter_class = LocationFilter
    filter_fields = ('index','date','start_date','end_date','strain','state','lineage','reference_id','mutation','amino_acid_position','gene','mutation_deletion',)
    search_fields = ('index','date','strain','state','lineage','reference_id','mutation','amino_acid_position','gene','mutation_deletion',)
    ordering_fields = ['index','date','strain','state','lineage','reference_id','mutation','amino_acid_position','gene','mutation_deletion',]
    def get_queryset(self):
         
        days = int(self.request.GET.get('days',3650))
        days=date.today()-timedelta(days=days)
        QuerySet = tsvfile.objects.filter(date__gte=days)
        return QuerySet


class AdvanceFilter(filters.FilterSet):
    class Meta:
        model = tsvfile
        fields = {'strain': ['iexact','exact', 'icontains','contains', 'startswith', 'isnull'], 'lineage': ['iexact', 'icontains','contains', 'startswith'], 
                'state': ['iexact', 'icontains','contains', 'startswith'], 'mutation_deletion': ['iexact', 'icontains','contains', 'startswith'], 
                'gene': ['iexact', 'icontains','contains', 'startswith'],'reference_id': ['iexact', 'icontains','contains', 'startswith'],
                'amino_acid_position': ['iexact', 'icontains', 'startswith', 'gte', 'lte', 'gt', 'lt'],'mutation': ['iexact', 'icontains','contains', 'startswith'], 
                'date': ['iexact', 'icontains','contains', 'startswith', 'lte', 'gte', 'lt', 'gt']}
        # filter_fields = ('index','date','start_date','end_date','strain','state','lineage','reference_id','mutation','amino_acid_position','gene','mutation_deletion',)

class AdvanceFiltering(ListAPIView):
    serializer_class = dataserializer
    pagination_class = LargeResultsSetPagination
    filter_backends = (DjangoFilterBackend,SearchFilter,OrderingFilter)
    filter_class = AdvanceFilter
    # filter_fields = LocationFilter
    filter_fields = ('index','date','start_date','end_date','strain','state','lineage','reference_id','mutation','amino_acid_position','gene','mutation_deletion',)
    search_fields = ('index','date','strain','state','lineage','reference_id','mutation','amino_acid_position','gene','mutation_deletion',)
    ordering_fields = ['index','date','strain','state','lineage','reference_id','mutation','amino_acid_position','gene','mutation_deletion',]
    def get_queryset(self):
         
        days = int(self.request.GET.get('days',3650))
        days=date.today()-timedelta(days=days)
        QuerySet = tsvfile.objects.filter(date__gte=days)
        return QuerySet

from django.db.models import Q
def getdata():
    # search = request.GET.get('search', "")
    search = "2021-09-17"
    page = 1
    per_page = 100
    start = (page-1)* per_page
    end = page*per_page
    QuerySet = tsvfile.objects.filter(Q(strain__icontains=search) | Q(lineage__icontains=search) | Q(date__icontains=search) | Q(mutation_deletion__icontains=search))
    print({"count":QuerySet.count(), "results": QuerySet.values()[0:5][start:end]})
    return QuerySet
getdata()




from django_filters import utils
class Myjangofilter(DjangoFilterBackend):
    # filter_backends = (DjangoFilterBackend,SearchFilter,OrderingFilter)
    def filter_queryset(self, request, queryset, view):
        filterset = self.get_filterset(request, queryset, view)
        if filterset is None:
            return queryset

        if not filterset.is_valid() and self.raise_exception:
            raise utils.translate_validation(filterset.errors)
        df  = pd.DataFrame.from_records(filterset.qs.values())
        
        df.to_csv(path,index=False)
        # print(path)
        return filterset.qs

class exportcsv(ListAPIView):
    serializer_class = dataserializer
    pagination_class = Filterpage
    filter_backends = (Myjangofilter,SearchFilter,OrderingFilter)
    filterset_class = LocationFilter
    
    filter_fields = ('index','date','start_date','end_date','strain','state','lineage','reference_id','mutation','amino_acid_position','gene','mutation_deletion',)
    search_fields = ('index','date','strain','state','lineage','reference_id','mutation','amino_acid_position','gene','mutation_deletion',)
    ordering_fields = ['index','date','strain','state','lineage','reference_id','mutation','amino_acid_position','gene','mutation_deletion',]
    def get_queryset(self):
        days = int(self.request.GET.get('days', 3650))
        days=date.today()-timedelta(days=days)
        QuerySet = tsvfile.objects.filter(date__gte=days)
        return QuerySet




class count(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    # paginated_by = 100
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count)
        ]))



class strainserializer(serializers.ModelSerializer):
    class Meta:
        model = tsvfile
        fields = ('strain',)
class uniqeseq(ListAPIView):
    serializer_class = strainserializer
    pagination_class = count
    def get_queryset(self):
        QuerySet = tsvfile.objects.order_by().values('strain').distinct()
        return QuerySet



class lineageserializer(serializers.ModelSerializer):
    class Meta:
        model = tsvfile
        fields = ('lineage',)
class uniqelineage(ListAPIView):
    serializer_class = lineageserializer
    pagination_class = LargeResultsSetPagination
    def get_queryset(self):
        QuerySet = tsvfile.objects.order_by().values('lineage').distinct()
        return QuerySet


class PangoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PangoVarsion
        fields = "__all__"


class Pangovarsionlist(ListAPIView):
    serializer_class = PangoSerializer
    pagination_class = LargeResultsSetPagination
    def get_queryset(self):
        QuerySet = PangoVarsion.objects.all().extra(select={'date':'DATE(date)'}).order_by('-id')[0:1]
        return QuerySet