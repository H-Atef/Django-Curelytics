from rest_framework import serializers
from . import models


class MedicinePriceSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.MedicinePriceInfo
        exclude=["id","search_q"]


class MedicineListSerializer(serializers.Serializer):
    medicines = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=False
    )

    