from django.urls import path
from . import views

urlpatterns = [
    path('diseases-symptoms/', views.DiseaseSymptomsToDB.as_view(), name='diseases-symptoms'),
    path('disease-predictions/<str:predictor_name>/', views.DiseasePrediction.as_view(), name='disease-predictions'),
    path('active-ingredient-diseases/', views.ActvIngDiseaseToDB.as_view(), name='active-ingredient-diseases'),
    path('active-ingredient-mappings/', views.ActiveIngredientMapper.as_view(), name='active-ingredient-mappings'),
    path('medicine-mappings/', views.MedicineMapper.as_view(), name='medicine-mappings'),
]
