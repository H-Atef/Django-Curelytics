from . import models,serializers
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from scrapers_classes import med_scraper_main as med_sc
from drf_yasg.utils import swagger_auto_schema






class MedicineViewSet(ModelViewSet):
    queryset=models.MedicineInfo.objects.all()
    serializer_class=serializers.MedicineSerializer

     # Built-in CRUD operations with swagger_auto_schema
    @swagger_auto_schema(tags=["Medicines Inventory"], operation_description="List all medicines")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=["Medicines Inventory"], operation_description="Retrieve a medicine")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(tags=["Medicines Inventory"], operation_description="Create a new medicine")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(tags=["Medicines Inventory"], operation_description="Update a medicine")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(tags=["Medicines Inventory"], operation_description="Partially update a medicine")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(tags=["Medicines Inventory"], operation_description="Delete a medicine")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        # Override to return the MedicineListSerializer for POST requests
        if self.action == 'scrape_medicines' and self.request.method == 'POST':
            return serializers.MedicineListSerializer  # Use the list serializer for POST
        return super().get_serializer_class()
    
    @swagger_auto_schema(
        method='post',
        tags=["Medicines Scraper"],
        operation_id="scrape_medicines",
        operation_description="Scrape medicines based on a list of medicines",
        request_body=serializers.MedicineListSerializer,
        responses={200: "List of scraped medicine info"}
    )
    @action(detail=False, methods=["POST"],url_path="scrape")
    def scrape_medicines(self, request):
        
        if request.method == "POST":
            # Use the new serializer for the POST request
            serializer = serializers.MedicineListSerializer(data=request.data)
            if serializer.is_valid():
                medicines = serializer.validated_data['medicines']

                scraper = med_sc.ScraperContext(med_sc.SCRAPER_MAPPING["DrugEye"])
                df = scraper.scrape_and_process(medicines)
                return Response(df.to_dict(orient="records"), status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





