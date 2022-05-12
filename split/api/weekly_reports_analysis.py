import re
import datetime
import pandas as pd
import datetime as dt
from django.db.models import Q
from django_filters import utils
from django.db.models import Count
from collections import OrderedDict
from datetime import date, timedelta
from dateutil.relativedelta import *
from rest_framework import serializers
from splitting.settings import BASE_DIR
from django.db.models.query import QuerySet
from rest_framework.response import Response
from split.models import nextstrain
from django_filters.constants import EMPTY_VALUES
from django_filters import rest_framework as filters
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView, RetrieveAPIView
from dateutil.relativedelta import relativedelta
from datetime import datetime

class lastfourmonthdataserializer(serializers.ModelSerializer):
    strain__count = serializers.IntegerField(read_only=True,)

    class Meta:
        model = nextstrain
        fields = ("collection_month", "strain__count",)

import datetime
from django.utils import timezone
class last_four_month(ListAPIView):
    serializer_class = lastfourmonthdataserializer
    def get_queryset(self):
        now = timezone.now()
        one_month_ago = datetime.datetime(now.year, now.month - 4,1)
        month_end = datetime.datetime(now.year, now.month, 1) - datetime.timedelta(seconds=1)
        QuerySet = nextstrain.objects.filter(date__gte=one_month_ago,date__lte=month_end).values(
            'collection_month').annotate(Count('strain', distinct=True)).order_by('date__year','date__month')
        return QuerySet


class stateslastthreemonthsdataserializer(serializers.ModelSerializer):
    strain__count = serializers.IntegerField(read_only=True,)

    class Meta:
        model = nextstrain
        fields = ("collection_month", "division", "strain__count",)

class stateslastthreemonthsdata(RetrieveAPIView):
    serializer_class = stateslastthreemonthsdataserializer
    def get(self, request):
        now = timezone.now()
        one_month_ago = datetime.datetime(now.year, now.month - 3,1)
        month_end = datetime.datetime(now.year, now.month, 1) - datetime.timedelta(seconds=1)
        QuerySet = nextstrain.objects.filter(date__gte=one_month_ago,date__lte=month_end).values(
            'collection_month','division').annotate(Count('strain', distinct=True)).order_by('date__month','-strain__count')
        d = {}
        for item in QuerySet:
            d.setdefault(item['collection_month'], []).append(item)
        list(d.values())
        return Response(d)

class submittinglablatestdataserializer(serializers.ModelSerializer):
    strain__count = serializers.IntegerField(read_only=True,)

    class Meta:
        model = nextstrain
        fields = ("collection_month", "submitting_lab", "strain__count",)

class submittinglablatestdata(RetrieveAPIView):
    serializer_class = submittinglablatestdataserializer
    def get(self, request):
        now = timezone.now()
        one_month_ago = datetime.datetime(now.year, now.month - 3,1)
        month_end = datetime.datetime(now.year, now.month, 1) - datetime.timedelta(seconds=1)
        QuerySet = nextstrain.objects.filter(date__gte=one_month_ago,date__lte=month_end).values(
            'collection_month','submitting_lab').annotate(Count('strain', distinct=True)).order_by('-strain__count')
        d = {}
        for item in QuerySet:
            d.setdefault(item['collection_month'], []).append(item)
        list(d.values())
        return Response(d)

def stacked_bar(QuerySet):
    res = QuerySet[0]
    res = list(res.keys())
    mnd = {}
    mnlist = []
    for dic in QuerySet:
        v = dic[res[0]]
        if v not in mnlist:
            mnlist.append(v)
    mnd[res[0]] = mnlist

    df = pd.DataFrame(QuerySet)
    df = df.set_index(res[0])
    dfT = df.T
    req_list = []
    for j in list(dfT.loc[res[1]].unique()):
        t = {}
        t[res[1]] = j
        t['value'] = []
        req_list.append(t)
    df2 = pd.DataFrame(QuerySet)
    df2 = df2.set_index([res[0], res[1]])
    for dic in req_list:
        lndic = dic[res[1]]
        months = mnd[res[0]]
        for month in months:
            if lndic in df2.loc[month].index:
                val = df2.loc[month, lndic][res[2]]
                dic['value'].append(val)
            else:
                dic['value'].append(0)
    c = []
    def column_sums(square):
        for i in req_list:
            c.append(i['value'])
        for j in req_list:
            return [sum(i) for i in zip(*square)]
    c = column_sums(c)
    b = []
    for j in req_list:
        yu = []
        b.append(j['value'])
        j['value1'] = []
        yu = [[round((100*x / y),2)for x, y in zip(lst, c)] for lst in b]
        for i in yu:
            j['value1'] = i
    req_list = sorted(req_list, key=lambda d: d['who_label'])
    return ({res[0]: mnd, res[1]: req_list})

class variant_status(RetrieveAPIView):
    def get(self, request):
        QuerySet1 = nextstrain.objects.filter(date__gte='2021-01-01',).values_list('collection_month').order_by('date__year','date__month').distinct()
        months = []
        for i in QuerySet1:
            months.extend(i)
        QuerySet = nextstrain.objects.filter(date__gte='2021-01-01',).values('collection_week','who_label').annotate(Count('strain', distinct=True)).order_by('collection_year')
        return Response(stacked_bar(QuerySet))

class last_four_month1(RetrieveAPIView):
    def get(self, request):
        now = timezone.now()
        one_month_ago = datetime.datetime(now.year, now.month - 4,1)
        month_end = datetime.datetime(now.year, now.month, 1) - datetime.timedelta(seconds=1)
        QuerySet = nextstrain.objects.filter(date__gte=one_month_ago,date__lte=month_end).values('collection_month','who_label').annotate(Count('strain', distinct=True)).order_by('collection_year','date__month','-who_label')
        d = stacked_bar(QuerySet)
        QuerySet1 = nextstrain.objects.values('who_label').distinct()
        labels = []
        for i in QuerySet1:
            labels.append(i['who_label'])
        for j in sorted(labels):
            if not any(d['who_label'] == j for d in d['who_label']):
                ad = {}
                ad["who_label"] = j
                ad['value'] = [0] * len(d['who_label'][0]['value'])
                ad['value1'] = [0.0] * len(d['who_label'][0]['value'])
                d['who_label'].append(ad)
            d['who_label'] = sorted(d['who_label'], key=lambda d: d['who_label'])
        return Response(d)

class weekwiselastthreemonths(RetrieveAPIView):
    def get(self, request):
        QuerySet1 = nextstrain.objects.filter(date__gte='2021-01-01',).values_list('collection_month').order_by('date__year','date__month').distinct()
        months = []
        for i in QuerySet1:
            months.extend(i)
        now = timezone.now()
        one_month_ago = datetime.datetime(now.year, now.month - 3,1)
        month_end = datetime.datetime(now.year, now.month, 1) - datetime.timedelta(seconds=1)
        QuerySet = nextstrain.objects.filter(date__gte=one_month_ago,date__lte=month_end).values('collection_week','who_label').annotate(Count('strain', distinct=True)).order_by('collection_year')
        d = stacked_bar(QuerySet)
        QuerySet1 = nextstrain.objects.values('who_label').distinct()
        labels = []
        for i in QuerySet1:
            labels.append(i['who_label'])
        for j in sorted(labels):
            if not any(d['who_label'] == j for d in d['who_label']):
                ad = {}
                ad["who_label"] = j
                ad['value'] = [0] * len(d['who_label'][0]['value'])
                ad['value1'] = [0.0] * len(d['who_label'][0]['value'])
                d['who_label'].append(ad)
            d['who_label'] = sorted(d['who_label'], key=lambda d: d['who_label'])
        return Response(d)

class RegionSerializer(serializers.ModelSerializer):
    strain__count = serializers.IntegerField(read_only=True,)

    class Meta:
        model = nextstrain
        fields = ("division","collection_week",'who_label', "strain__count",)
from itertools import groupby

def key_func(k):
    return k['region_type']
class Regionwisedata(RetrieveAPIView):
    def get(self, request):
        a = []; b = []; c = {}; d = {}
        QuerySet = nextstrain.objects.filter(date__gte="2021-01-01").values('region_type','collection_week','who_label').annotate(Count('strain', distinct=True)).order_by('collection_year')
        QuerySet = sorted(QuerySet, key=key_func)
        for key, value in groupby(QuerySet, key_func):
            b.append(list(value))
            for i in b:
                c[key] = i
        for i in c:
            for items in c[i]:
                del items['region_type']
            d[i] = stacked_bar(c[i])
        QuerySet1 = nextstrain.objects.values('who_label').distinct()
        labels = []
        for i in QuerySet1:
            labels.append(i['who_label'])
        for i in d.values():
            for j in sorted(labels):
                if not any(d['who_label'] == j for d in i['who_label']):
                    ad = {}
                    ad["who_label"] = j
                    ad['value'] = [0] * len(i['who_label'][0]['value'])
                    ad['value1'] = [0.0] * len(i['who_label'][0]['value'])
                    i['who_label'].append(ad)
            i['who_label'] = sorted(i['who_label'], key=lambda d: d['who_label'])
        return Response(d)


def collection_month(k):
    return k['collection_month']
class VariantStatusbyStates(RetrieveAPIView):
    def get(self, request):
        a = []; b = []; c = {}; d = {}
        now = timezone.now()
        one_month_ago = datetime.datetime(now.year, now.month - 2,1)
        month_end = datetime.datetime(now.year, now.month, 1) - datetime.timedelta(seconds=1)
        QuerySet = nextstrain.objects.filter(date__gte=one_month_ago,date__lte=month_end).values('collection_month','division','who_label').annotate(Count('strain', distinct=True)).order_by('who_label')
        QuerySet = sorted(QuerySet, key=collection_month)
        for key, value in groupby(QuerySet, collection_month):
            b.append(list(value))
            for i in b:
                c[key] = i
        for i in c:
            for items in c[i]:
                del items['collection_month']
            d[i] = stacked_bar(c[i])
        QuerySet1 = nextstrain.objects.values('who_label').distinct()
        labels = []
        for i in QuerySet1:
            labels.append(i['who_label'])
        for i in d.values():
            for j in sorted(labels):
                if not any(d['who_label'] == j for d in i['who_label']):
                    ad = {}
                    ad["who_label"] = j
                    ad['value'] = [0] * len(i['who_label'][0]['value'])
                    ad['value1'] = [0.0] * len(i['who_label'][0]['value'])
                    i['who_label'].append(ad)
            i['who_label'] = sorted(i['who_label'], key=lambda d: d['who_label'])
        return Response(d)

class Regionwisedata2022(RetrieveAPIView):
    def get(self, request):
        a = []; b = []; c = {}; d = {}
        QuerySet = nextstrain.objects.filter(date__gte="2022-01-01").values('region_type','collection_week','who_label').annotate(Count('strain', distinct=True)).order_by('collection_year')
        QuerySet = sorted(QuerySet, key=key_func)
        for key, value in groupby(QuerySet, key_func):
            b.append(list(value))
            for i in b:
                c[key] = i
        for i in c:
            for items in c[i]:
                del items['region_type']
            d[i] = stacked_bar(c[i])
        QuerySet1 = nextstrain.objects.values('who_label').distinct()
        labels = []
        for i in QuerySet1:
            labels.append(i['who_label'])
        for i in d.values():
            for j in sorted(labels):
                if not any(d['who_label'] == j for d in i['who_label']):
                    ad = {}
                    ad["who_label"] = j
                    ad['value'] = [0] * len(i['who_label'][0]['value'])
                    ad['value1'] = [0.0] * len(i['who_label'][0]['value'])
                    i['who_label'].append(ad)
            i['who_label'] = sorted(i['who_label'], key=lambda d: d['who_label'])
        return Response(d)