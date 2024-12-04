from . import models, serializers
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from scrapers_classes import med_scraper_main as med_sc


class MedicinePriceViewSet(ModelViewSet):
    # Define the queryset to fetch all MedicinePriceInfo objects
    queryset = models.MedicinePriceInfo.objects.all()
    serializer_class = serializers.MedicinePriceSerializer

    def get_serializer_class(self):
        # Override to return the MedicineListSerializer for POST requests in the 'scrape_medicine_price_info' action
        if self.action == 'scrape_medicine_price_info' and self.request.method == 'POST':
            return serializers.MedicineListSerializer  # Use the list serializer for POST
        return super().get_serializer_class()

    @action(detail=False, methods=["GET", "POST"])
    def scrape_medicine_price_info(self, request):
        # Handle GET request - returns an empty list
        if request.method == "GET":
            return Response([], status=status.HTTP_200_OK)

        # Handle POST request - scrape the medicine prices based on provided medicines
        elif request.method == "POST":
            # Validate the posted data with the MedicineListSerializer
            serializer = serializers.MedicineListSerializer(data=request.data)
            if serializer.is_valid():
                medicines = serializer.validated_data['medicines']

                # Initialize the scraper and process the data
                scraper = med_sc.ScraperContext(med_sc.SCRAPER_MAPPING["DrugEyeTitan"])
                df = scraper.scrape_and_process(medicines)
                
                # Return the scraped data as a list of dictionaries
                return Response(df.to_dict(orient="records"), status=status.HTTP_200_OK)
            else:
                # Return validation errors if the serializer is invalid
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    @action(detail=False, methods=["GET"])
    def search_by_drug_name(self, request, drug_name):
        # Validate the input drug name parameter
        if not drug_name:
            return Response({"detail": "Drug name is required for search."}, status=status.HTTP_400_BAD_REQUEST)

        # Search for medicines containing the drug name (case-insensitive)
        medicines = models.MedicinePriceInfo.objects.filter(drug_name__icontains=drug_name)

        if medicines.exists():
            # Serialize the search results
            serializer = serializers.MedicinePriceSerializer(medicines, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # Return a 404 if no medicines are found
            return Response({"detail": "No matching medicines found."}, status=status.HTTP_404_NOT_FOUND)
        
    def get_updated_med_prices(self, request):
        # Collect unique drug names from the database
        unique_names = set()
        medicines = models.MedicinePriceInfo.objects.all()

        for medicine in medicines:
            drug_name = medicine.search_q  # Extract the search query (drug name)
            unique_names.add(drug_name)

        # Delete all existing records in the MedicinePriceInfo table
        models.MedicinePriceInfo.objects.all().delete()

        # Initialize the scraper to get updated data
        scraper = med_sc.ScraperContext(med_sc.SCRAPER_MAPPING["DrugEyeTitan"])

        # Scrape and process the updated data based on unique drug names
        df = scraper.scrape_and_process(unique_names)

        # Convert the resulting DataFrame to a list of dictionaries
        updated_data = df.to_dict(orient="records")

        # Return the updated data as a response
        return Response(updated_data, status=status.HTTP_200_OK)
