import datetime
# import sqlalchemy
import pandas as pd
from django.shortcuts import render
from rest_framework import generics
from sqlalchemy import create_engine
from rest_framework import serializers
from rest_framework.response import Response
from split.models import tsvfile, nextstrain
from django.core.management.base import BaseCommand
from pymongo import MongoClient
# Create your views here.


class Command(BaseCommand):
    def handle(self, *args, **options):
        df = pd.read_csv(
            'C:/Users/sampa/Desktop/lineage_substitution_deletion_report.tsv', sep='\t', header=0)
        # print(df)
        engine = create_engine('sqlite:///db.sqlite3')
        df.to_sql(tsvfile._meta.db_table, con=engine,
                  index=True, if_exists='replace')


class fileserializer(serializers.Serializer):
    file = serializers.FileField()
    # nextstraindata = serializers.FileField()


class uploadserializer(serializers.Serializer):

    class Meta:
        model = tsvfile
        fields = "__all__"


Alpha = ['B.1.1.7', 'Q.']
Omicron = ['B.1.1.529', 'BA.']
Delta = ['B.1.617.2', 'AY.']
Beta = ['B.1.351']
Gamma = ['P.1']
Lambda = ['C.']
Mu = ['B.1.621', 'BB.']
VUM = ['B.1.1.318', 'C.1.2', 'B.1.640']
FMV = [
    'AV.1', 'AT.1', 'P.2', 'P.3', 'R.1', 'B.1.466.2', 'B.1.1.519', 'C.36.3',
    'B.1.214.2', 'B.1.427', 'B.1.429', 'B.1.1.523',
    'B.1.619', 'B.1.620', 'B.1.526', 'B.1.525', 'B.1.617.1', 'B.1.630'
]
none = ['None']
Other = Alpha+Omicron+Delta+Beta+Gamma+Lambda+Mu+VUM+FMV+none


class adddata(generics.CreateAPIView):
    serializer_class = fileserializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data['file']
        reader = pd.read_csv(file, sep='\t', header=0)
        reader = reader.sort_values('date')

        reader.loc[~(reader.lineage.str.contains(
            '|'.join(Other))),  'Class'] = 'Other'
        reader.loc[(reader.lineage.str.contains(
            '|'.join(Alpha))),  'Class'] = 'Alpha'
        reader.loc[(reader.lineage.str.contains(
            '|'.join(Omicron))),  'Class'] = 'Omicron'
        reader.loc[(reader.lineage.str.contains(
            '|'.join(Delta))),  'Class'] = 'Delta'
        reader.loc[(reader.lineage.str.contains(
            '|'.join(Beta))),  'Class'] = 'Beta'
        reader.loc[(reader.lineage.str.contains(
            '|'.join(Gamma))),  'Class'] = 'Gamma'
        reader.loc[(reader.lineage.str.contains(
            '|'.join(Lambda))),  'Class'] = 'Lambda'
        reader.loc[(reader.lineage.str.contains(
            '|'.join(Mu))),  'Class'] = 'Mu'
        reader.loc[(reader.lineage.str.contains(
            '|'.join(VUM))),  'Class'] = 'VUM'
        reader.loc[(reader.lineage.str.contains(
            '|'.join(FMV))),  'Class'] = 'FMV'
        reader.loc[(reader.lineage.str.contains(
            '|'.join(none))),  'Class'] = 'None'

        # reader['date'] = pd.to_datetime(reader.date, format='%Y-%m-%d').dt.date
        reader['date1'] = pd.to_datetime(reader.date, format='%Y-%m-%d')
        reader['year'] = reader['date1'].dt.strftime('%Y')
        reader['week_number'] = reader['date1'].dt.strftime('W%V-%Y')
        reader['month_number'] = reader['date1'].dt.strftime('%B-%Y')
        reader["month_number"] = reader["month_number"].str[0:3] + reader["month_number"].str[-5:]
        reader.loc[reader.week_number ==
                   "W52-2022", "week_number"] = "W01-2022"

        reader[['gene', 'reference_id', 'amino_acid_position', 'mutation']
               ] = reader['mutation/deletion'].str.split(':([a-zA-Z*]+)([0-9]+)', n=1, expand=True)
        reader.rename(
            columns={'mutation/deletion': 'mutation_deletion'}, inplace=True)
        
        engine = create_engine('sqlite:///db.sqlite3')

        tsvfile(reader.to_sql(tsvfile._meta.db_table,
                con=engine, index=True, if_exists='replace'))

        returnmsg = {"message": "success"}
        # except Exception as e:
        #     returnmsg = {"message": "Importing error"}
        return Response(returnmsg)



class fileserializer1(serializers.Serializer):
    file = serializers.FileField()

class adddata1(generics.CreateAPIView):
    serializer_class = fileserializer1

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data['file']
        reader1 = pd.read_csv(file, sep='\t', header=0,)
        reader1['date1'] = pd.to_datetime(reader1.date, format='%Y-%m-%d')
        reader1.loc[reader1.collection_week ==
                   "W52-2022", "collection_week"] = "W01-2022"
        reader1['collection_year'] = reader1['date1'].dt.strftime('%Y')
        reader1 = reader1[["strain","date", "division","region_type","submitting_lab","collection_month","collection_week","collection_year","WHO_label","lineage"]]
        # reader1 = reader1.reset_index(inplace = True)
        engine = create_engine('sqlite:///db.sqlite3')

        nextstrain(reader1.to_sql(nextstrain._meta.db_table,
                con=engine, index=True, if_exists='replace'))
        print(reader1)
        # nextstrain.objects.all().delete()
        # objs = [
        #     nextstrain(
        #         index=row.index,
        #         strain=row.strain,
        #         date=row.date,
        #         state=row.division,
        #         submitting_lab=row.submitting_lab,
        #         collection_month=row.collection_month,
        #         collection_week=row.collection_week,
        #         collection_year=row.year,
        #         who_label=row.WHO_label,
        #         lineage=row.lineage,
        #     )
        #     for index, row in reader1.iterrows()
        # ]
        # nextstrain.objects.bulk_create(objs)
        returnmsg = {"message": "success"}
        return Response(returnmsg)
