from . import models,serializers
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from .scraper_helper import med_scraper_main as med_sc






class MedicineViewSet(ModelViewSet):
    queryset=models.MedicineInfo.objects.all()
    serializer_class=serializers.MedicineSerializer

    def get_serializer_class(self):
        # Override to return the MedicineListSerializer for POST requests
        if self.action == 'scrape_medicines' and self.request.method == 'POST':
            return serializers.MedicineListSerializer  # Use the list serializer for POST
        return super().get_serializer_class()

    @action(detail=False, methods=["GET", "POST"])
    def scrape_medicines(self, request):
        if request.method == "GET":
            # Return an empty list with HTTP 200 status
            return Response([], status=status.HTTP_200_OK)

        elif request.method == "POST":
            # Use the new serializer for the POST request
            serializer = serializers.MedicineListSerializer(data=request.data)
            if serializer.is_valid():
                medicines = serializer.validated_data['medicines']

                scraper = med_sc.ScraperContext(med_sc.SCRAPER_MAPPING["DrugEye"])
                df = scraper.scrape_and_process(medicines)
                return Response(df.to_dict(orient="records"), status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





