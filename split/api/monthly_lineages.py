from collections import defaultdict
import operator
from re import L
from os import stat
import pandas as pd
from pyparsing import line
from functools import reduce
from split.models import tsvfile
from datetime import date, timedelta
from django.db.models import Count, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveAPIView


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
    return ({res[0]: mnd, res[1]: req_list})


class MonthlyLineageStackBar(RetrieveAPIView):
    def get(self, request):
        default_lineages = ['B.1.1.7', 'B.1.351', 'B.1.351.2', 'B.1.351.3',
                            'P.1', 'P.1.1', 'P.1.2', 'B.1.617.2', 'AY.1',
                            'AY.2', 'B.1.525',
                            'B.1.526', 'B.1.617.1', 'C.37']
        days = int(self.request.GET.get('days', 3650))
        year = self.request.GET.get('year', "2021,2022")
        days = date.today()-timedelta(days=days)
        lineage = self.request.GET.get('lineage', "")
        strain = self.request.GET.get('strain',)
        state = self.request.GET.get('state',)
        mutaion_deletion = self.request.GET.get('mutaion_deletion',)
        gene = self.request.GET.get('gene',)
        reference_id = self.request.GET.get('reference_id',)
        amino_acid_position = self.request.GET.get('amino_acid_position',)
        mutation = self.request.GET.get('mutation',)
        date_search = self.request.GET.get('date_search')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        obj = tsvfile.objects
        if(lineage):
            # obj = obj.filter(lineage__in=["AY.1,B"])
            obj = obj.filter(lineage__in=lineage.split(','))
        if(state):
            obj = obj.filter(state__icontains=state)
        if(strain):
            obj = obj.filter(strain__icontains=strain)
        if(mutaion_deletion):
            obj = obj.filter(mutaion_deletion__icontains=mutaion_deletion)
        if(gene):
            obj = obj.filter(gene__icontains=gene)
        if(reference_id):
            obj = obj.filter(reference_id__icontains=reference_id)
        if(date_search):
            obj = obj.filter(date__icontains=date_search)
        if(amino_acid_position):
            obj = obj.filter(
                amino_acid_position__icontains=amino_acid_position)
        if(mutation):
            obj = obj.filter(mutation__icontains=mutation)
        if(start_date):
            obj = obj.filter(date__gte=start_date)
        if(end_date):
            obj = obj.filter(date__lte=end_date)
        if(year):
            obj = obj.filter(year__in=year.split(','))
        if(not lineage) or lineage == "undefined" or lineage == None:
            QuerySet = obj.filter(date__gte=days, lineage__in=default_lineages).values(
                'month_number', 'lineage').annotate(Count('strain', distinct=True)).order_by('year','date__month')
            return Response(stacked_bar(QuerySet))
        QuerySet = obj.filter(date__gte=days, lineage__in=lineage.split(',')).values(
            'month_number', 'lineage').annotate(Count('strain', distinct=True)).order_by('year','date__month')
        return Response(stacked_bar(QuerySet))


result = defaultdict(int)
class MonthlyDistribution(RetrieveAPIView):
    def get(self, request):
        days = int(self.request.GET.get('days', 3650))
        year = self.request.GET.get('year', "2021,2022")
        days = date.today()-timedelta(days=days)
        lineage = self.request.GET.get('lineage', "")
        strain = self.request.GET.get('strain',)
        state = self.request.GET.get('state',)
        mutaion_deletion = self.request.GET.get('mutaion_deletion',)
        gene = self.request.GET.get('gene',)
        reference_id = self.request.GET.get('reference_id',)
        amino_acid_position = self.request.GET.get('amino_acid_position',)
        mutation = self.request.GET.get('mutation',)
        date_search = self.request.GET.get('date_search')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        obj = tsvfile.objects
        if(lineage):
            obj = obj.filter(lineage__in=lineage.split(','))
        if(state):
            obj = obj.filter(state__icontains=state)
        if(strain):
            obj = obj.filter(strain__icontains=strain)
        if(mutaion_deletion):
            obj = obj.filter(mutaion_deletion__icontains=mutaion_deletion)
        if(gene):
            obj = obj.filter(gene__icontains=gene)
        if(reference_id):
            obj = obj.filter(reference_id__icontains=reference_id)
        if(date_search):
            obj = obj.filter(date__icontains=date_search)
        if(amino_acid_position):
            obj = obj.filter(
                amino_acid_position__icontains=amino_acid_position)
        if(mutation):
            obj = obj.filter(mutation__icontains=mutation)
        if(start_date):
            obj = obj.filter(date__gte=start_date)
        if(end_date):
            obj = obj.filter(date__lte=end_date)
        if(year):
            obj = obj.filter(year__in=year.split(','))
        # if(days):
        #     obj = obj.filter(date__gte='2022-01-01')
        QuerySet = obj.values(
            'month_number',).annotate(Count('strain', distinct=True)).order_by('date')
        # l = []
        result.clear()
        for d in QuerySet:
            result[d['month_number']] += int(d['strain__count'])
        l = ({'month_number': name, 'strain__count': value}
             for name, value in result.items())
        # print(l)
        # l.clear()
        return Response(l)
