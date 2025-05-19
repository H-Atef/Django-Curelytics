from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import APIException, ValidationError
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Disease Predictor
from .classes.disease_predictors.process_org_dataset import OriginalDatasetPre
from .classes.disease_predictors.disease_predictor_main import MedDataContext

# Active Ingredients Mapper
from .classes.active_ingredients_mapper.dataset_generator.active_ingredients_generator import ActiveIngredientsDatasetGenerator
from .classes.active_ingredients_mapper.disease_mapper import DiseaseActvIngMapper

# Medicine Mapper
from .classes.medicine_mapper.active_ingredient_scraper import DrugEyeActvIngScraper

from . import models, serializers

class DiseaseSymptomsToDB(APIView):
    """
    This view saves disease symptoms data to the database if
    they don't already exist and display them if exist.
    """

    @swagger_auto_schema(tags=["Medicine Advisor"], operation_id="get_disease_symptoms")
    def get(self, request):
        try:
            disease_symptom_data = models.DiseaseSymptom.objects.all()
            serializer = serializers.DiseaseSymptomSerializer(disease_symptom_data, many=True)
            return Response(serializer.data)
        except Exception as e:
            raise APIException(f"Error retrieving data from the database: {str(e)}")

    @swagger_auto_schema(tags=["Medicine Advisor"], operation_id="save_disease_symptoms")
    def post(self, request):
        try:
            dataset_processor = OriginalDatasetPre()
            df = dataset_processor.process_dataset()
            df.columns = ["disease", "symptom", "disease_class"]

            existing_data = models.DiseaseSymptom.objects.all()
            serializer = serializers.DiseaseSymptomSerializer(existing_data, many=True)

            if serializer.data != df.to_dict(orient="records"):
                instances = [models.DiseaseSymptom(**row.to_dict()) for _, row in df.iterrows()]
                models.DiseaseSymptom.objects.bulk_create(instances)

            return Response(df.to_dict(orient="records"))
        except Exception as e:
            raise APIException(f"Error processing and saving data: {str(e)}")


class DiseasePrediction(APIView):
    """
    This view handles the disease prediction process based on symptoms.
    """

    @swagger_auto_schema(
        tags=["Medicine Advisor"],
        operation_id="predict_disease_from_symptoms",
        manual_parameters=[
            openapi.Parameter('predictor_name', openapi.IN_PATH, description="Predictor name", type=openapi.TYPE_STRING)
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'symptoms': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING))
            },
            required=['symptoms']
        ),
        responses={200: "Prediction Results"}
    )
    def post(self, request, predictor_name):
        try:
            symptoms = request.data.get("symptoms", [])
            if not symptoms:
                return Response({"error": "No symptoms provided"}, status=400)

            predictor_context = MedDataContext()
            predictor_context.set_predictor(predictor_name)
            predictions = predictor_context.predict(symptoms)

            if not predictions:
                return Response({"error": "Failure in the prediction process"}, status=500)

            cases = {}
            for i, case in enumerate(predictions):
                result = {disease: confidence for disease, confidence in case}
                cases[f"Case{i + 1}"] = result

            return Response(cases)
        except Exception as e:
            raise APIException(f"Error during disease prediction: {str(e)}")


class ActvIngDiseaseToDB(APIView):
    """
    This view saves active ingredients with their associated diseases data to the database 
    if they don't already exist and display them if exist.
    """

    @swagger_auto_schema(tags=["Medicine Advisor"], operation_id="get_active_ingredient_disease_data")
    def get(self, request):
        try:
            actvIng_disease_data = models.ActvIngDisease.objects.all()
            serializer = serializers.ActvIngDiseaseSerializer(actvIng_disease_data, many=True)
            return Response(serializer.data)
        except Exception as e:
            raise APIException(f"Error retrieving data from the database: {str(e)}")

    @swagger_auto_schema(tags=["Medicine Advisor"], operation_id="save_active_ingredient_disease_data")
    def post(self, request):
        try:
            dataset_generator = ActiveIngredientsDatasetGenerator()
            df = dataset_generator.generate_csv_file()
            df.columns = ["option_one_treatment", "option_two_treatment", "option_three_treatment", "disease"]

            existing_data = models.ActvIngDisease.objects.all()
            serializer = serializers.ActvIngDiseaseSerializer(existing_data, many=True)

            if serializer.data != df.to_dict(orient="records"):
                instances = [models.ActvIngDisease(**row.to_dict()) for _, row in df.iterrows()]
                models.ActvIngDisease.objects.bulk_create(instances)

            return Response(df.to_dict(orient="records"))
        except Exception as e:
            raise APIException(f"Error processing and saving data: {str(e)}")


class ActiveIngredientMapper(APIView):

    @swagger_auto_schema(
        tags=["Medicine Advisor"],
        operation_id="map_diseases_to_active_ingredients",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'diseases': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING))
            },
            required=['diseases']
        ),
        responses={200: "Mapped active ingredients"}
    )
    def post(self, request):
        try:
            diseases_to_be_mapped = request.data.get("diseases", [])
            if not diseases_to_be_mapped:
                raise ValidationError("The 'diseases' field is required and should not be empty.")

            actv_mapper = DiseaseActvIngMapper()
            result_dict = actv_mapper.map_pridected_diseases_to_actv(diseases_to_be_mapped)
            return Response(result_dict, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "An error occurred while processing the request.", "details": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MedicineMapper(APIView):
    @swagger_auto_schema(
        tags=["Medicine Advisor"],
        operation_id="map_active_ingredients_to_medicines",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'actv_ing_list': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING))
            },
            required=['actv_ing_list']
        ),
        responses={200: "Retrieved medicines"}
    )
    def post(self, request):
        actv_ing_list = request.data.get("actv_ing_list", [])
        scraper = DrugEyeActvIngScraper()
        retrieved_medicines = scraper.search_medicines(actv_ing_list)
        return Response(retrieved_medicines)
