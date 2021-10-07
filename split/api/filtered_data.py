from django.db.models.query import QuerySet
import pandas as pd
from django.db.models import fields
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
# from django_filters.rest_framework import DjangoFilterBackend
from pandas.core.frame import DataFrame
from rest_framework import generics, pagination, serializers
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from split.models import tsvfile
# import sqlalchemy
from sqlalchemy import create_engine
from split.api.filetrbackend import DjangoFilterBackend
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
path = f'{BASE_DIR}/download/tsvfile{new_file}.csv'
class LargeResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
class Filterpage(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    paginated_by = 100
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('path', path)
        ]))


from datetime import date, timedelta
from django_filters import rest_framework as filters
class LocationFilter(filters.FilterSet):
    d = date.today()-timedelta(days=7)
    id = filters.NumberFilter(lookup_expr='icontains')
    strain = filters.CharFilter(lookup_expr='icontains')
    lineage = filters.CharFilter(lookup_expr='icontains')
    reference_id = filters.CharFilter(lookup_expr='icontains')
    mutation = filters.CharFilter(lookup_expr='icontains')
    amine_acid_position = filters.CharFilter(lookup_expr='icontains')
    gene = filters.CharFilter(lookup_expr='icontains')
    date = filters.CharFilter(lookup_expr='icontains')
    start_date = filters.DateFilter(field_name="date",lookup_expr="gte")
    end_date = filters.DateFilter(field_name="date",lookup_expr="lte")
    # past_data = filters(date__=d)
    # d=date.today()-timedelta(days=7)
    class Meta:
        model = tsvfile
        fields = ['id','date','start_date','end_date','strain','lineage','reference_id','mutation','amine_acid_position','gene',]


class dataserializer(serializers.ModelSerializer):
    class Meta:
        model = tsvfile
        fields = ('id','date','strain','lineage','reference_id','mutation','amine_acid_position','gene')

class LineageFilter(RetrieveAPIView):
    serializer_class = dataserializer
    def get(self, request,lineage):
        A = tsvfile.objects.filter(lineage=lineage)
        serializer = dataserializer(A, many=True)
        return Response({"data": serializer.data})

class dateserializer(serializers.ModelSerializer):
    class Meta:
        model = tsvfile
        fields = ('id','date')
class max_date(RetrieveAPIView):
    serializer_class = dateserializer
    def get(self, request):
        A = tsvfile.objects.order_by('date').first()
        serializer = dateserializer(A, many=True)
        return Response({"data": serializer.data})


class MutationFilter(RetrieveAPIView):
    serializer_class = dataserializer
    def get(self, request):
        A = tsvfile.objects.values('strain').distinct()
        count = tsvfile.objects.values('strain').distinct().count()
        serializer = dataserializer(A, many=True)
        return Response({"data": serializer.data,"count": count})


class Filter1(RetrieveAPIView):
    serializer_class = dataserializer
    def get(self, request):
        A = tsvfile.objects.all()[0:20]
        serializer = dataserializer(A, many=True)
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
class filter2(ListAPIView):
    serializer_class = FilterSerializer1
    pagination_class = LargeResultsSetPagination
    filter_backends = (DjangoFilterBackend,SearchFilter,OrderingFilter)
    filter_class = LocationFilter
    filter_fields = ('id','date','start_date','end_date','strain','lineage','reference_id','mutation','amine_acid_position','gene',)
    search_fields = ('id','date','strain','lineage','reference_id','mutation','amine_acid_position','gene',)
    ordering_fields = ['id','date','strain','lineage','reference_id','mutation','amine_acid_position','gene',]
    def get_queryset(self):
        days = int(self.request.GET.get('days',3650))
        days=date.today()-timedelta(days=days)
        QuerySet = tsvfile.objects.filter(date__gte=days)
        return QuerySet
    

from django.db.models import Q


class Filter(APIView):
    pagination_class = LargeResultsSetPagination
    serializer_class = FilterSerializer
    
    def post(self,request):
        strain = request.data.get('strain')
        lineage = request.data.get('lineage')
        mutation = request.data.get('mutation')
        gene = request.data.get('gene')
        reference_id = request.data.get('reference_id')
        amine_acid_position = request.data.get('amine_acid_position')
        search = request.data.get('search', "")
        page = int(request.data.get('page', 1))
        per_page = 100
        start = (page -1)* per_page
        end = page*per_page
        if search:
            A = tsvfile.objects.filter(Q(mutation__icontains=search) | Q(lineage__icontains=search) | Q(strain__icontains=search) | Q(reference_id__icontains=search) | Q(amine_acid_position__icontains=search) | Q(gene__icontains=search))
            serializer = FilterSerializer(A[start:end], many=True)
        if strain:
            A = tsvfile.objects.filter(strain__icontains=strain)
            serializer = FilterSerializer(A[start:end], many=True)
        if lineage:
            A = tsvfile.objects.filter(lineage__icontains=lineage)
            serializer = FilterSerializer(A[start:end], many=True)
        if gene:
            A = tsvfile.objects.filter(gene__icontains=gene)
            serializer = FilterSerializer(A[start:end], many=True)
        if reference_id:
            A = tsvfile.objects.filter(reference_id__icontains=reference_id)
            serializer = FilterSerializer(A[start:end], many=True)
        if mutation:
            A = tsvfile.objects.filter(mutation__icontains=mutation)
            serializer = FilterSerializer(A[start:end], many=True)
        if amine_acid_position:
            A = tsvfile.objects.filter(amine_acid_position__icontains=amine_acid_position)
            serializer = FilterSerializer(A[start:end], many=True)


        if strain and lineage:
            A = tsvfile.objects.filter(lineage__icontains=lineage,strain__icontains=strain)
            serializer = FilterSerializer(A[start:end], many=True)
        if strain and gene:
            A = tsvfile.objects.filter(gene__icontains=gene,strain__icontains=strain)
            serializer = FilterSerializer(A[start:end], many=True)
        if strain and reference_id:
            A = tsvfile.objects.filter(reference_id__icontains=reference_id,strain__icontains=strain)
            serializer = FilterSerializer(A[start:end], many=True)
        if strain and mutation:
            A = tsvfile.objects.filter(strain__icontains=strain,mutation__icontains=mutation)
            serializer = FilterSerializer(A[start:end], many=True)
        if strain and amine_acid_position:
            A = tsvfile.objects.filter(strain__icontains=strain,amine_acid_position__icontains=amine_acid_position)
            serializer = FilterSerializer(A[start:end], many=True)


        if lineage and gene:
            A = tsvfile.objects.filter(gene__icontains=gene,lineage__icontains=lineage)
            serializer = FilterSerializer(A[start:end], many=True)
        if lineage and reference_id:
            A = tsvfile.objects.filter(reference_id__icontains=reference_id,lineage__icontains=lineage)
            serializer = FilterSerializer(A[start:end], many=True)
        if lineage and mutation:
            A = tsvfile.objects.filter(mutation__icontains=mutation,lineage__icontains=lineage)
            serializer = FilterSerializer(A[start:end], many=True)
        if lineage and amine_acid_position:
            A = tsvfile.objects.filter(amine_acid_position__icontains=amine_acid_position,lineage__icontains=lineage)
            serializer = FilterSerializer(A[start:end], many=True)


        if mutation and gene:
            A = tsvfile.objects.filter(mutation__icontains=mutation,gene__icontains=gene,)
            serializer = FilterSerializer(A[start:end], many=True)
        if mutation and amine_acid_position:
            A = tsvfile.objects.filter(amine_acid_position__icontains=amine_acid_position,mutation__icontains=mutation)
            serializer = FilterSerializer(A[start:end], many=True)
        if mutation and reference_id:
            A = tsvfile.objects.filter(reference_id__icontains=reference_id,mutation__icontains=mutation)
            serializer = FilterSerializer(A[start:end], many=True)


        if gene and amine_acid_position:
            A = tsvfile.objects.filter(amine_acid_position__icontains=amine_acid_position,gene__icontains=gene)
            serializer = FilterSerializer(A[start:end], many=True)
        if gene and reference_id:
            A = tsvfile.objects.filter(reference_id__icontains=reference_id,gene__icontains=gene)
            serializer = FilterSerializer(A[start:end], many=True)

        if reference_id and amine_acid_position:
            A = tsvfile.objects.filter(amine_acid_position__icontains=amine_acid_position,reference_id__icontains=reference_id)
            serializer = FilterSerializer(A[start:end], many=True)
        if mutation and lineage and strain and reference_id and amine_acid_position and gene:
            A = tsvfile.objects.filter(mutation__icontains=mutation,lineage__icontains=lineage,strain__icontains=strain,reference_id__icontains=reference_id,amine_acid_position__icontains=amine_acid_position,gene__icontains=gene)
            serializer = FilterSerializer(A[start:end], many=True)
        if ((not mutation) or (mutation == 'undefined')) and ((not lineage) or (lineage == 'undefined')) and ((not strain) or (strain == 'undefined')) and ((not gene) or (gene == 'undefined')) and ((not reference_id) or (reference_id == 'undefined')) and ((not amine_acid_position) or (amine_acid_position == 'undefined')):
            A = tsvfile.objects.all()
            serializer = FilterSerializer(A[start:end], many=True)
        return Response({"data": serializer.data})


class Myjangofilter(DjangoFilterBackend):
    def filter_queryset(self, request, queryset, view):
        filterset = self.get_filterset(request, queryset, view)
        if filterset is None:
            return queryset

        if not filterset.is_valid() and self.raise_exception:
            raise utils.translate_validation(filterset.errors)
        df  = pd.DataFrame.from_records(filterset.qs.values())
        
        df.to_csv(path,index=False)
        print(path)
        return filterset.qs

class exportcsv(ListAPIView):
    serializer_class = dataserializer
    pagination_class = Filterpage
    filter_backends = [Myjangofilter]
    filterset_class = LocationFilter
    
    filter_fields = ('id','date','start_date','end_date','strain','lineage','reference_id','mutation','amine_acid_position','gene',)
    search_fields = ('id','date','strain','lineage','reference_id','mutation','amine_acid_position','gene',)
    ordering_fields = ['id','date','strain','lineage','reference_id','mutation','amine_acid_position','gene',]
    def get_queryset(self):
        days = int(self.request.GET.get('days',3650))
        days=date.today()-timedelta(days=days)
        QuerySet = tsvfile.objects.filter(date__gte=days)
        return QuerySet

