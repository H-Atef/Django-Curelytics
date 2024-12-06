from django.urls import path
from . import views

urlpatterns = [
    path('diseases-symptoms-db/', views.DiseaseSymptomsToDB.as_view(), name='diseases-symptoms-list'),
    path('predict-disease/<str:predictor_name>/', views.DiseasePrediction.as_view(), name='predict-disease'),
    path('actv-diseases-db/', views.ActvIngDiseaseToDB.as_view(), name='actv-diseases-list'),
    path('actv-ing-mapper/', views.ActiveIngredientMapper.as_view(), name='actv-ing-mapper'),
    path('medicine-mapper/', views.MedicineMapper.as_view(), name='medicine-mapper'),
]
