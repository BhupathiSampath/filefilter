import pandas as pd
from split.models import tsvfile
from django.db.models import Count
from collections import OrderedDict
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


class CountPagination(PageNumberPagination):  
    page_size = 1000
    page_size_query_param = 'page_size'
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            # ('results', data)
        ]))


class LineageCountSerializer(serializers.ModelSerializer):
    class Meta:
        model = tsvfile
        fields = ('lineage',)
class UniqeLineageCount(ListAPIView):
    serializer_class = LineageCountSerializer
    pagination_class = CountPagination
    filter_backends = (DjangoFilterBackend,SearchFilter,OrderingFilter)
    filterset_class = LocationFilter
    
    filter_fields = ('index','date','start_date','end_date','strain','reference_id','mutation','amino_acid_position','gene','mutation_deletion',)
    search_fields = ('index','date','strain','state','lineage','reference_id','mutation','amino_acid_position','gene','mutation_deletion',)
    ordering_fields = ['index','date','strain','state','lineage','reference_id','mutation','amino_acid_position','gene','mutation_deletion',]
    def get_queryset(self):
        QuerySet = tsvfile.objects.order_by().values('lineage').distinct()
        # QuerySet = tsvfile.objects.order_by().values('lineage').annotate(Count('lineage', distinct=False))
        return QuerySet



class ResultsPagination(PageNumberPagination):  
    page_size = 1000
    page_size_query_param = 'page_size'
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            # ('count', self.page.paginator.count),
            ('results', data)
        ]))


class UniqueLineageStrainSerializer(serializers.ModelSerializer):
    strain__count = serializers.IntegerField(read_only=True,)
    class Meta:
        model = tsvfile
        fields = ('lineage','strain__count')

class UniqueLineageStrain(ListAPIView):
    serializer_class = UniqueLineageStrainSerializer
    pagination_class = ResultsPagination
    filter_backends = (DjangoFilterBackend,SearchFilter,OrderingFilter)
    filterset_class = LocationFilter
    
    filter_fields = ('index','date','start_date','end_date','strain','reference_id','mutation','amino_acid_position','gene','mutation_deletion',)
    search_fields = ('index','date','strain','state','lineage','reference_id','mutation','amino_acid_position','gene','mutation_deletion',)
    ordering_fields = ['index','date','strain','state','lineage','reference_id','mutation','amino_acid_position','gene','mutation_deletion',]
    def get_queryset(self):
        QuerySet = tsvfile.objects.order_by().values('lineage').annotate(Count('strain', distinct=True))
        return QuerySet