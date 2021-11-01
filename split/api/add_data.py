from django.shortcuts import render
import pandas as pd
from rest_framework import generics
# import sqlalchemy
from sqlalchemy import create_engine
from split.models import tsvfile,PangoVarsion
from django.core.management.base import BaseCommand

# Create your views here.
class Command(BaseCommand):
    def handle(self, *args, **options):
        df = pd.read_csv('C:/Users/sampa/Desktop/lineage_substitution_deletion_report.tsv', sep='\t', header=0)
        # print(df)
        engine = create_engine('sqlite:///db.sqlite3')
        df.to_sql(tsvfile._meta.db_table, con=engine,index=True, if_exists='replace')


import datetime
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import serializers
class fileserializer(serializers.Serializer):
    file = serializers.FileField()
    file_version = serializers.FileField()
class uploadserializer(serializers.Serializer):
    
    class Meta:
        model = tsvfile
        fields = "__all__"


class adddata(generics.CreateAPIView):
    serializer_class = fileserializer
    
    def post(self, request, *args, **kwargs):
        # data = self.get_initial()
        # file = data.get('file')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception = True)
        file = serializer.validated_data['file']
        file_version = serializer.validated_data['file_version']
        reader = pd.read_csv(file, sep='\t', header=0)
        reader1 = pd.read_csv(file_version, header=0, nrows=1)
        # reader[['mutation_deletion']] = reader['mutation/deletion']
        # reader[['gene','mutation_deletion']] = reader['mutation_deletion'].str.split(':',n=1, expand=True)
        # print(reader)
        # reader[['reference_id','amino_acid_position','mutation']] = reader['mutation_deletion'].str.split('([*][a-zA-Z]+)([0-9]+)', n=1, expand=True)
        # print(reader)
        # reader[['reference_id','amino_acid_position','mutation']] = (re.split('\d+([0-9]+)', reader["mutation_deletion"], 2))
        reader[['gene','reference_id','amino_acid_position','mutation']] = reader['mutation/deletion'].str.split(':([a-zA-Z*]+)([0-9]+)', n=1, expand=True)
        reader.rename(columns = {'mutation/deletion':'mutation_deletion'}, inplace = True)
        engine = create_engine('sqlite:///db.sqlite3')
        tsvfile(reader.to_sql(tsvfile._meta.db_table, con=engine,index=True, if_exists='replace'))
        # PangoVarsion(reader1.to_sql(PangoVarsion._meta.db_table, con=engine,index=True, if_exists='replace'))

        # objs = [
        #     tsvfile(
        #         strain = row.strain,
        #         lineage = row.lineage,
        #         gene = row.gene,
        #         reference_id = row.reference_id,
        #         amino_acid_position = row.amino_acid_position,
        #         mutation = row.mutation,
        #         date = row.date,
        #         state = row.state,
        #         mutation_deletion = row.mutation_deletion
        #     )
        #     for index, row in reader.iterrows()
            
        # ]
        # # try:
        # tsvfile.objects.bulk_create(objs)
        


        objs = [
            PangoVarsion(
                version = row.version,
                pangolin_version = row.pangolin_version,
                pangoLEARN_version = row.pangoLEARN_version,
                pango_version = row.pango_version,
                date = datetime.datetime.today()
            )
            for index, row in reader1.iterrows()
            
        ]
        # try:
        PangoVarsion.objects.bulk_create(objs)
        returnmsg = {"message": "success"}
        # except Exception as e:
        #     returnmsg = {"message": "Importing error"}
        return Response(returnmsg)
            


