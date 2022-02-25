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

class MonthlyLineageStackBar(RetrieveAPIView):
    def get(self, request):
        default_lineages = ['B.1.1.7', 'B.1.351', 'B.1.351.2', 'B.1.351.3', 'P.1', 'P.1.1', 'P.1.2', 'B.1.617.2', 'AY.1', 'AY.2', 'B.1.525', 'B.1.526', 'B.1.617.1', 'C.37']
        days = int(self.request.GET.get('days',3650))
        year = self.request.GET.get('year',"202")
        days=date.today()-timedelta(days=days)
        lineage = self.request.GET.get('lineage',"")
        strain = self.request.GET.get('strain',)
        state = self.request.GET.get('state',)
        mutaion_deletion = self.request.GET.get('mutaion_deletion',)
        gene = self.request.GET.get('gene',)    
        reference_id = self.request.GET.get('reference_id',)
        amino_acid_position = self.request.GET.get('amino_acid_position',)
        mutation = self.request.GET.get('mutation',)
        date_search = self.request.GET.get('date_search')
        from_date = self.request.GET.get('from_date')
        to_date = self.request.GET.get('to_date')
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
            obj = obj.filter(amino_acid_position__icontains=amino_acid_position)
        if(mutation):
            obj = obj.filter(mutation__icontains=mutation)
        if(from_date):
            obj = obj.filter(date__gte=from_date)
        if(to_date):
            obj = obj.filter(date__lte=to_date)
        if(not lineage) or lineage == "undefined" or lineage == None:
            QuerySet = tsvfile.objects.filter(date__gte=days, month_number__icontains=year, 
            	lineage__in=default_lineages)\
            .values('month_number','lineage').annotate(Count('strain', distinct=True)).order_by('date')
            # res = QuerySet[0]
            # res = list(QuerySet.keys())
            mnd = {}
            mnlist = [] 
            for dic in QuerySet:
                v = dic['month_number']
                if v not in mnlist:
                    mnlist.append(v)
            mnd['month_number'] = mnlist
            df = pd.DataFrame(QuerySet)
            df = df.set_index('month_number')
            dfT = df.T
            req_list = []
            for j in list(dfT.loc['lineage'].unique()):
                t = {}
                t['lineage'] = j
                t['value'] = []
                req_list.append(t)
            df2 = pd.DataFrame(QuerySet)
            df2 = df2.set_index(['month_number', 'lineage']);
            for dic in req_list:
                lndic = dic['lineage']
                months = mnd['month_number']
                for month in months:
                    if lndic in df2.loc[month].index:
                        val = df2.loc[month, lndic]['strain__count']
                        dic['value'].append(val)
                    else :
                        dic['value'].append(0)
            return Response({"month": mnd, "lineage": req_list})
        QuerySet = obj.filter(date__gte=days, month_number__icontains=year, lineage__in=lineage.split(',')).values('month_number','lineage').annotate(Count('strain', distinct=True)).order_by('date__year','date__month')
        mnd = {}
        mnlist = []
        for dic in QuerySet:
            v = dic['month_number']
            if v not in mnlist:
                mnlist.append(v)
        mnd['month_number'] = mnlist
        df = pd.DataFrame(QuerySet)
        df = df.set_index('month_number')
        dfT = df.T
        req_list = []
        for j in list(dfT.loc['lineage'].unique()):
            t = {}
            t['lineage'] = j
            t['value'] = []
            req_list.append(t)
        df2 = pd.DataFrame(QuerySet)
        df2 = df2.set_index(['month_number', 'lineage']);
        for dic in req_list:
            lndic = dic['lineage']
            months = mnd['month_number']
            for month in months:
                if lndic in df2.loc[month].index:
                    val = df2.loc[month, lndic]['strain__count']
                    dic['value'].append(val)
                else:
                    dic['value'].append(0)
        return Response({"month": mnd, "lineage": req_list})