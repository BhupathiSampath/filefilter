from django.db.models.query_utils import Q
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework import serializers
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from split.api.filtered_data import LocationFilter
from split.models import tsvfile
import pandas as pd
from django.db.models import Count
from datetime import date, timedelta

class LargeResultsSetPagination(PageNumberPagination):  
    page_size = 100
    page_size_query_param = 'page_size'


class MutationDistributionSerializer(serializers.ModelSerializer):
    mutation_deletion__count = serializers.IntegerField(read_only=True,)
    class Meta:
        model = tsvfile
        fields = ("state","mutation_deletion__count",)


class StatesMutationDistribution(ListAPIView):
    serializer_class = MutationDistributionSerializer
    filter_backends = (DjangoFilterBackend,SearchFilter,OrderingFilter)
    filterset_class = LocationFilter
    
    filter_fields = ('index','date','start_date','end_date','strain','reference_id','mutation','amino_acid_position','gene','mutation_deletion',)
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
    def get_queryset(self):
        QuerySet = tsvfile.objects.values('state').annotate(Count('strain', distinct=True))
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
        print(QuerySet)
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
        QuerySet = tsvfile.objects.filter(date__gte=days,month_number__icontains=year).values('month_number').annotate(Count('strain', distinct=True)).order_by('date__year','date__month')
        return QuerySet