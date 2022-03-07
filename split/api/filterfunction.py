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
from split.api.filtered_data import ListFilter
# from split.api.monthly_lineages import stacked_bar
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


def queryhub_api(search):
    obj = tsvfile.objects
    if(search["lineage"]):
        obj = obj.filter(lineage__in=search['lineage'])
    if(search["state"]):
        obj = obj.filter(state__in=search['state'])
    if(search["mutation"]):
        obj = obj.filter(reduce(
            operator.and_, (Q(mutation_deletion__contains=x) for x in search["mutation"])))
    if(search["start_date"]):
        obj = obj.filter(date__gte=search['start_date'])
    if(search["end_date"]):
        obj = obj.filter(date__lte=search['end_date'])
    lineage_count = obj.values('lineage').annotate(
        Count('strain', distinct=True))
    state_count = obj.values('state').annotate(Count('strain', distinct=True))
    return {"lineage": list(lineage_count), "state": list(state_count)}


def week_structure(QuerySet):
    week = {}
    mnlist = []
    for dic in QuerySet:
        v = dic['week_number']
        if v not in mnlist:
            mnlist.append(v)
    week['week_number'] = mnlist
    df = pd.DataFrame(QuerySet)
    df = df.set_index('week_number')
    dfT = df.T
    week_lineage_list = []
    for j in list(dfT.loc['Class'].unique()):
        t = {}
        t['Class'] = j
        t['value'] = []
        week_lineage_list.append(t)
    df2 = pd.DataFrame(QuerySet)
    df2 = df2.set_index(['week_number', 'Class'])
    for dic in week_lineage_list:
        lndic = dic['Class']
        months = week['week_number']
        for month in months:
            if lndic in df2.loc[month].index:
                val = df2.loc[month, lndic]['strain__count']
                dic['value'].append(val)
            else:
                dic['value'].append(0)
    return({"week": week, "weekly_lineage": week_lineage_list})


class LineageClassificationWeekly(RetrieveAPIView):
    def get(self, request):
        days = int(self.request.GET.get('days', 3650))
        year = self.request.GET.get('year', "2021,2022")
        days = date.today()-timedelta(days=days)
        lineage = self.request.GET.get('lineage')
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
        QuerySet = obj.filter(date__gte=days,).values(
        'week_number', 'Class').annotate(Count('strain', distinct=True)).order_by('year')
        # QuerySet = obj.filter(date__gte=days,).values(
        #     'week_number', 'Class').annotate(Count('strain', distinct=True)).order_by('date__year')
        return Response(stacked_bar(QuerySet))


def month_structure(QuerySet1):
    mnd = {}
    mnlist = []
    for dic in QuerySet1:
        v = dic['month_number']
        if v not in mnlist:
            mnlist.append(v)
    mnd['month_number'] = mnlist
    df = pd.DataFrame(QuerySet1)
    df = df.set_index('month_number')
    dfT = df.T
    req_list = []
    for j in list(dfT.loc['Class'].unique()):
        t = {}
        t['Class'] = j
        t['value'] = []
        req_list.append(t)
    df2 = pd.DataFrame(QuerySet1)
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
    return({"month": mnd, "lineage": req_list})


class LineageClassificationMonth(RetrieveAPIView):
    def get(self, request):
        days = int(self.request.GET.get('days', 3650))
        year = self.request.GET.get('year', "2021,2022")
        days = date.today()-timedelta(days=days)
        lineage = self.request.GET.get('lineage')
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
        QuerySet = obj.filter(date__gte=days,).values('month_number', 'Class').annotate(Count('strain', distinct=True))
        return Response(stacked_bar(QuerySet))


def weekly_lineage(QuerySet):
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
    for j in list(dfT.loc['lineage'].unique()):
        t = {}
        t['lineage'] = j
        t['value'] = []
        req_list.append(t)
    df2 = pd.DataFrame(QuerySet)
    df2 = df2.set_index(['week_number', 'lineage'])
    for dic in req_list:
        lndic = dic['lineage']
        months = mnd['week_number']
        for month in months:
            if lndic in df2.loc[month].index:
                val = df2.loc[month, lndic]['strain__count']
                dic['value'].append(val)
            else:
                dic['value'].append(0)
    return Response({"week": mnd, "lineage": req_list})


class WeeklyLineageStackBar(RetrieveAPIView):
    def get(self, request):
        default_lineages = ["B.1.1.7", "B.1.351", "B.1.617.2", "AY.1", "AY.2", "AY.3", "AY.4",
                            "B.1.351", "P.1", "B.1.1.318", 'B.1.466.2', 'B.1.1.318', 'C.1.2', 'B.1.640', 'B.1.1.519', 'C.36.3', "B.1.1.529", "BA.1", "BA.2", "BA.3"]
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
            QuerySet = obj.filter(date__gte=days,
                                  lineage__in=default_lineages)\
                .values('week_number', 'lineage').annotate(Count('strain', distinct=True)).order_by('year')
            # QuerySet = obj.filter(date__gte=days,
            #                       lineage__in=default_lineages)\
            #     .values('week_number', 'lineage').annotate(Count('strain', distinct=True)).order_by('date__year')
            # mnd = {}
            # mnlist = []
            # for dic in QuerySet:
            #     v = dic['week_number']
            #     if v not in mnlist:
            #         mnlist.append(v)
            # mnd['week_number'] = mnlist
            # df = pd.DataFrame(QuerySet)
            # df = df.set_index('week_number')
            # dfT = df.T
            # req_list = []
            # for j in list(dfT.loc['lineage'].unique()):
            #     t = {}
            #     t['lineage'] = j
            #     t['value'] = []
            #     req_list.append(t)
            # df2 = pd.DataFrame(QuerySet)
            # df2 = df2.set_index(['week_number', 'lineage'])
            # for dic in req_list:
            #     lndic = dic['lineage']
            #     months = mnd['week_number']
            #     for month in months:
            #         if lndic in df2.loc[month].index:
            #             val = df2.loc[month, lndic]['strain__count']
            #             dic['value'].append(val)
            #         else:
            #             dic['value'].append(0)
            return Response(stacked_bar(QuerySet))
        QuerySet = obj.filter(date__gte=days, lineage__in=lineage.split(
        ',')).values('week_number', 'lineage').annotate(Count('strain', distinct=True)).order_by('year')
        # QuerySet = obj.filter(date__gte=days, lineage__in=lineage.split(
        #     ',')).values('week_number', 'lineage').annotate(Count('strain', distinct=True)).order_by('date__year')
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
        for j in list(dfT.loc['lineage'].unique()):
            t = {}
            t['lineage'] = j
            t['value'] = []
            req_list.append(t)
        df2 = pd.DataFrame(QuerySet)
        df2 = df2.set_index(['week_number', 'lineage'])
        for dic in req_list:
            lndic = dic['lineage']
            months = mnd['week_number']
            for month in months:
                if lndic in df2.loc[month].index:
                    val = df2.loc[month, lndic]['strain__count']
                    dic['value'].append(val)
                else:
                    dic['value'].append(0)
        return Response(stacked_bar(QuerySet))


class StatesLineageClassification(ListAPIView):
    def get(self, request):
        days = int(self.request.GET.get('days', 3650))
        year = self.request.GET.get('year', "2021,2022")
        days = date.today()-timedelta(days=days)
        lineage = self.request.GET.get('lineage')
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
        QuerySet = obj.filter(date__gte=days).values(
            'state', 'Class').annotate(Count('strain', distinct=True))
        # mnd = {}
        # mnlist = []
        # for dic in QuerySet:
        #     v = dic['state']
        #     if v not in mnlist:
        #         mnlist.append(v)
        # mnd['state'] = mnlist
        # df = pd.DataFrame(QuerySet)
        # df = df.set_index('state')
        # dfT = df.T
        # req_list = []
        # for j in list(dfT.loc['Class'].unique()):
        #     t = {}
        #     t['Class'] = j
        #     t['value'] = []
        #     req_list.append(t)
        # df2 = pd.DataFrame(QuerySet)
        # df2 = df2.set_index(['state', 'Class'])
        # for dic in req_list:
        #     lndic = dic['Class']
        #     months = mnd['state']
        #     for month in months:
        #         if lndic in df2.loc[month].index:
        #             val = df2.loc[month, lndic]['strain__count']
        #             dic['value'].append(val)
        #         else:
        #             dic['value'].append(0)
        return Response(stacked_bar(QuerySet))


def states_lineage(QuerySet2):
    mnd = {}
    mnlist = []
    for dic in QuerySet2:
        v = dic['state']
        if v not in mnlist:
            mnlist.append(v)
    mnd['state'] = mnlist
    df = pd.DataFrame(QuerySet2)
    df = df.set_index('state')
    dfT = df.T
    req_list = []
    for j in list(dfT.loc['Class'].unique()):
        t = {}
        t['Class'] = j
        t['value'] = []
        req_list.append(t)
    df2 = pd.DataFrame(QuerySet2)
    df2 = df2.set_index(['state', 'Class'])
    for dic in req_list:
        lndic = dic['Class']
        months = mnd['state']
        for month in months:
            if lndic in df2.loc[month].index:
                val = df2.loc[month, lndic]['strain__count']
                dic['value'].append(val)
            else:
                dic['value'].append(0)
    return({"state": mnd, "state_lineage": req_list})
