from . import models, serializers
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from scrapers_classes import med_scraper_main as med_sc


class MedicinePriceViewSet(ModelViewSet):
    queryset = models.MedicinePriceInfo.objects.all()
    serializer_class = serializers.MedicinePriceSerializer
    
    # Built-in CRUD operations with swagger_auto_schema
    @swagger_auto_schema(tags=["Price Tracker"], 
                         operation_id="medicine_prices_list",
                         operation_description="List all medicine prices")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=["Price Tracker"],
                         operation_id="medicine_prices_retrieve",
                         operation_description="Retrieve a medicine price by ID")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(tags=["Price Tracker"],
                         operation_id="medicine_prices_create",
                         operation_description="Create a new medicine price entry")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(tags=["Price Tracker"], 
                         operation_id="medicine_prices_update",
                         operation_description="Update a medicine price entry")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(tags=["Price Tracker"],
                         operation_id="medicine_prices_partial_update",
                         operation_description="Partially update a medicine price entry")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(tags=["Price Tracker"],
                         operation_id="medicine_prices_delete",
                         operation_description="Delete a medicine price entry")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == 'scrape_medicine_price_info' and self.request.method == 'POST':
            return serializers.MedicineListSerializer
        return super().get_serializer_class()

    @swagger_auto_schema(
        method='post',
        tags=["Medicines Scraper"],
        operation_id="scrape_medicine_price_info",
        operation_description="Scrape medicine prices based on a list of medicines",
        request_body=serializers.MedicineListSerializer,
        responses={200: "List of scraped medicine price info"}
    )
    @action(detail=False, methods=["POST"],url_path="scrape")
    def scrape_medicine_price_info(self, request):
        """
        POST: Scrape medicine price info using provided medicines list.
        """
        if request.method == "POST":
            serializer = serializers.MedicineListSerializer(data=request.data)
            if serializer.is_valid():
                medicines = serializer.validated_data['medicines']
                scraper = med_sc.ScraperContext(med_sc.SCRAPER_MAPPING["DrugEyeTitan"])
                df = scraper.scrape_and_process(medicines)
                return Response(df.to_dict(orient="records"), status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        method='get',
        tags=["Price Tracker"],
        operation_id="search_by_drug_name",
        operation_description="Search medicine prices by drug name",
        responses={200: serializers.MedicinePriceSerializer(many=True)}
    )
    @action(detail=False, methods=["GET"], url_path='search/(?P<drug_name>[^/.]+)')
    def search_by_drug_name(self, request, drug_name):
        """
        GET: Search medicines by partial drug name match.
        """
        if not drug_name:
            return Response({"detail": "Drug name is required for search."}, status=status.HTTP_400_BAD_REQUEST)
        medicines = models.MedicinePriceInfo.objects.filter(drug_name__icontains=drug_name)
        if medicines.exists():
            serializer = serializers.MedicinePriceSerializer(medicines, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "No matching medicines found."}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        method='put',
        tags=["Price Tracker"],
        operation_id="update_medicine_prices",
        operation_description="Update medicine prices by scraping unique drug names",
        responses={200: "Updated list of medicine prices"}
    )
    @action(detail=False, methods=["PUT"],url_path="update-prices")
    def update_med_prices(self, request):
        """
        PUT: Scrape and update medicine prices for unique drug names in the database.
        """
        unique_names = set()
        medicines = models.MedicinePriceInfo.objects.all()
        for medicine in medicines:
            drug_name = medicine.search_q
            unique_names.add(drug_name)
        models.MedicinePriceInfo.objects.all().delete()
        scraper = med_sc.ScraperContext(med_sc.SCRAPER_MAPPING["DrugEyeTitan"])
        df = scraper.scrape_and_process(unique_names)
        updated_data = df.to_dict(orient="records")
        return Response(updated_data, status=status.HTTP_200_OK)
