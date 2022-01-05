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

class StatesLineageDistribution(RetrieveAPIView):
    def get(self, request):
        df = pd.DataFrame(list(tsvfile.objects.values("state", "lineage")))
        df = df['lineage'].groupby(df['state']).nunique().reset_index(name="count")
        # df = pd.DataFrame(df)
        QuerySet = df.to_dict("r")
        return Response({"data": QuerySet})

class Frequency(RetrieveAPIView):
    pagination_class = LargeResultsSetPagination
    def get(self, request):
        df = pd.DataFrame(list(tsvfile.objects.all().values()))
        df = df.groupby(["state", 'lineage', "mutation_deletion"]).size().reset_index(name="count")
        df = pd.DataFrame(df)
        QuerySet = df.to_dict("r")
        print(QuerySet)
        return Response({"data": QuerySet})