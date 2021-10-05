from django.shortcuts import render
import pandas as pd
from rest_framework import generics
# import sqlalchemy
from sqlalchemy import create_engine
from split.models import tsvfile
from django.core.management.base import BaseCommand

# Create your views here.
class Command(BaseCommand):
    def handle(self, *args, **options):
        df = pd.read_csv('C:/Users/sampa/Desktop/lineage_substitution_deletion_report.tsv', sep='\t', header=0)
        # print(df)
        engine = create_engine('sqlite:///db.sqlite3')
        df.to_sql(tsvfile._meta.db_table, con=engine,index=True, if_exists='replace')



from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import serializers
class fileserializer(serializers.Serializer):
    file = serializers.FileField()
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
        reader = pd.read_csv(file, sep='\t', header=0)
        reader[['gene','reference_id','amine_acid_position','mutation']] = reader['mutation/deletion'].str.split(':([a-zA-Z]+)([0-9]+)', n=1, expand=True)

        # engine = create_engine('sqlite:///db.sqlite3')
        # tsvfile(reader.to_sql(tsvfile._meta.db_table, con=engine,index=True, if_exists='replace'))

        # tsvfile.objects.bulk_create([tsvfile(strain=reader.strain,lineage=reader.lineage,mutation_deletion=reader.mutation_deletion)])
        # for index, row in reader.iterrows():
        #     new_file = tsvfile(
        #         strain = row['strain'],
        #         lineage = row['lineage'],
        #         mutation_deletion = row['mutation_deletion']
        #     )
        
        # bulk = tsvfile.objects.bulk_create([reader])
        # print(reader)
        objs = [
            tsvfile(
                strain = row.strain,
                lineage = row.lineage,
                gene = row.gene,
                reference_id = row.reference_id,
                amine_acid_position = row.amine_acid_position,
                mutation = row.mutation,
                date = row.date
            )
            for index, row in reader.iterrows()
            
        ]
        # try:
        tsvfile.objects.bulk_create(objs)
        returnmsg = {"message": "success"}
        # except Exception as e:
        #     returnmsg = {"message": "Importing error"}
        return Response(returnmsg)
            


