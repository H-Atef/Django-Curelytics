from rest_framework import serializers
from . import models


class DiseaseSymptomSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.DiseaseSymptom
        exclude=["id"]


class ActvIngDiseaseSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.ActvIngDisease
        exclude=["id"]


    