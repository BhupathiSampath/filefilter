from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from split.models import tsvfile
import pandas as pd


class LargeResultsSetPagination(PageNumberPagination):  
    page_size = 100
    page_size_query_param = 'page_size'

class StatesMutationDistribution(RetrieveAPIView):
    # pagination_class = LargeResultsSetPagination
    def get(self, request):
        df = pd.DataFrame(list(tsvfile.objects.all().values()))
        df = df['mutation_deletion'].groupby(df['state']).nunique().reset_index(name="count")
        # df = pd.DataFrame(df)
        QuerySet = df.to_dict("series")
        return Response({"data": QuerySet})


# class FrequencySerializer(serializers.ModelSerializer):
#     count = serializers.IntegerField(read_only=True,)
#     # b = serializers.IntegerField(read_only=True,)
#     class Meta:
#         model = tsvfile
#         fields = ("state","lineage","gene","count")

class Frequency(RetrieveAPIView):
    pagination_class = LargeResultsSetPagination
    def get(self, request):
        df = pd.DataFrame(list(tsvfile.objects.all().values()))
        df = df.groupby(["state", 'lineage', "mutation_deletion"]).size().reset_index(name="count")
        df = pd.DataFrame(df)
        QuerySet = df.to_dict("r")
        print(QuerySet)
        return Response({"data": QuerySet})