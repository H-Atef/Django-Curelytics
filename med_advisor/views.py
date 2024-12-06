from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import APIException,ValidationError
from rest_framework import status



#Disease Predictor
from .classes.disease_predictors.process_org_dataset import OriginalDatasetPre
from .classes.disease_predictors.disease_predictor_main import MedDataContext

#Active Ingredients Mapper
from .classes.active_ingredients_mapper.dataset_generator.active_ingredients_generator import ActiveIngredientsDatasetGenerator
from .classes.active_ingredients_mapper.disease_mapper import DiseaseActvIngMapper


#Medicine Mapper
from .classes.medicine_mapper.active_ingredient_scraper import DrugEyeActvIngScraper


from . import models, serializers

class DiseaseSymptomsToDB(APIView):
    """
    This view saves disease symptoms data to the database if
      they don't already exist and display them if exist.
    """

    def get(self, request):
        try:
            # Retrieve all disease-symptom records from the database
            disease_symptom_data = models.DiseaseSymptom.objects.all()
            serializer = serializers.DiseaseSymptomSerializer(disease_symptom_data, many=True)
            return Response(serializer.data)

        except Exception as e:
            # Handle any errors while fetching data from the database
            raise APIException(f"Error retrieving data from the database: {str(e)}")

    def post(self, request):
        try:
            # Process the dataset
            dataset_processor = OriginalDatasetPre()
            df = dataset_processor.process_dataset()
            df.columns = ["disease", "symptom", "disease_class"]

            # Check if the dataset already exists in the database
            existing_data = models.DiseaseSymptom.objects.all()
            serializer = serializers.DiseaseSymptomSerializer(existing_data, many=True)

            # If the data does not match, insert the DataFrame to the database
            if serializer.data != df.to_dict(orient="records"):
                instances = []
                for index, row in df.iterrows():
                    disease = row.to_dict()
                    instance = models.DiseaseSymptom(**disease)
                    instances.append(instance)

                # Save the data to the database in bulk
                models.DiseaseSymptom.objects.bulk_create(instances)

            return Response(df.to_dict(orient="records"))

        except Exception as e:
            # Handle any errors during dataset processing or database operation
            raise APIException(f"Error processing and saving data: {str(e)}")


class DiseasePrediction(APIView):
    """
    This view handles the disease prediction process based on symptoms.
    """

    def get(self, request, predictor_name):
        # For GET request, return an empty response or provide any additional info if required
        return Response({})

    def post(self, request, predictor_name):
        try:
            # Extract symptoms from the request
            symptoms = request.data.get("symptoms", [])

            
            if not symptoms:
                return Response({"error": "No symptoms provided"}, status=400)

            # Initialize the prediction context
            predictor_context = MedDataContext()
            predictor_context.set_predictor(predictor_name)

            # Predict the disease(s) based on the provided symptoms
            predictions = predictor_context.predict(symptoms)

            # Handle the case when predictions are empty
            if not predictions:
                return Response({"error": "Failure in the prediction process"}, status=500)

            cases = {}
            for i, case in enumerate(predictions):
                result = {disease: confidence for disease, confidence in case}
                cases[f"Case{i + 1}"] = result

            return Response(cases)

        except Exception as e:
            # Handle any errors during the prediction process
            raise APIException(f"Error during disease prediction: {str(e)}")
        


class ActvIngDiseaseToDB(APIView):
    """
    This view saves active ingredients with thier associated diseases data to the database 
    if they don't already exist and display them if exist.
    """

    def get(self, request):
        try:
            # Retrieve all actvIng-disease records from the database
            actvIng_disease_data = models.ActvIngDisease.objects.all()
            serializer = serializers.ActvIngDiseaseSerializer(actvIng_disease_data, many=True)
            return Response(serializer.data)

        except Exception as e:
            # Handle any errors while fetching data from the database
            raise APIException(f"Error retrieving data from the database: {str(e)}")

    def post(self, request):
        try:
            # Process the dataset
            dataset_generator = ActiveIngredientsDatasetGenerator()
            df = dataset_generator.generate_csv_file()
            df.columns = ["primary_treatment", "alt_treatment_one","alt_treatment_two","disease"]

            # Check if the dataset already exists in the database
            existing_data = models.ActvIngDisease.objects.all()
            serializer = serializers.ActvIngDiseaseSerializer(existing_data, many=True)

            # If the data does not match, insert the DataFrame to the database
            if serializer.data != df.to_dict(orient="records"):
                instances = []
                for index, row in df.iterrows():
                    actv = row.to_dict()
                    instance = models.ActvIngDisease(**actv)
                    instances.append(instance)

                # Save the data to the database in bulk
                models.ActvIngDisease.objects.bulk_create(instances)

            return Response(df.to_dict(orient="records"))

        except Exception as e:
            # Handle any errors during dataset processing or database operation
            raise APIException(f"Error processing and saving data: {str(e)}")



class ActiveIngredientMapper(APIView):

    def get(self, request):
        """
        Handle GET requests. 
        This endpoint currently returns an empty dictionary.
        """
        try:
            # Return a successful response with an empty dictionary
            return Response({}, status=status.HTTP_200_OK)
        except Exception as e:
            # Log the exception and return an internal server error response
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        """
        Handle POST requests to map diseases to active ingredients.
        It expects a list of diseases in the 'diseases' field of the request body.
        """
        try:
            # Retrieve the list of diseases to be mapped from the request
            diseases_to_be_mapped = request.data.get("diseases", [])
            
            if not diseases_to_be_mapped:
                # If the 'diseases' field is empty or missing, return a bad request error
                raise ValidationError("The 'diseases' field is required and should not be empty.")
            
            # Instantiate the mapper to map diseases to active ingredients
            actv_mapper = DiseaseActvIngMapper()
            
            # Perform the mapping
            result_dict = actv_mapper.map_pridected_diseases_to_actv(diseases_to_be_mapped)
            
            # Return the mapping result as a response with status 200 (OK)
            return Response(result_dict, status=status.HTTP_200_OK)
        
        except ValidationError as e:
            # Return a bad request error if validation fails (e.g., missing or invalid 'diseases' field)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            # Handle any unexpected errors and return an internal server error response
            return Response({"error": "An error occurred while processing the request.", "details": str(e)}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class MedicineMapper(APIView):
    def get(self,request):
        return Response({})
    
    def post(self, request):
        actv_ing_list= request.data.get("actv_ing_list", [])
        scraper=DrugEyeActvIngScraper()
        retrieved_medicines=scraper.search_medicines(actv_ing_list)
        
        return Response(retrieved_medicines)