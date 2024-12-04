from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("medicine-price-info", views.MedicinePriceViewSet, basename="medicine-price-info")

urlpatterns = [

    path("scrape-medicine-price-info/", views.MedicinePriceViewSet.as_view({"get": "scrape_medicine_price_info", "post": "scrape_medicine_price_info"}), name="scrape-medicine-price-info"),
    
    path("get-updated-med-prices/", views.MedicinePriceViewSet.as_view({"get": "get_updated_med_prices"}), name="get-updated-med-prices"),
    
    path("search-by-drug-name/<str:drug_name>/", views.MedicinePriceViewSet.as_view({"get": "search_by_drug_name"}), name="search-by-drug-name"),
] + router.urls
