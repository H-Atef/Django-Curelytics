from rest_framework import serializers
from . import models


class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.MedicineInfo
        exclude=["id"]


class MedicineListSerializer(serializers.Serializer):
    medicines = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=False
    )

    