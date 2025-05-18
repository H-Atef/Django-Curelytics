from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("medicine-price-info", views.MedicinePriceViewSet, basename="medicine-price-info")

urlpatterns = [
path("scrape/", views.MedicinePriceViewSet.as_view({"post": "scrape_medicine_price_info"}), name="medicine-price-info-scrape"),

path("updated-prices/", views.MedicinePriceViewSet.as_view({"get": "get_updated_med_prices"}), name="medicine-price-info-updated-prices"),

path("search/<str:drug_name>/", views.MedicinePriceViewSet.as_view({"get": "search_by_drug_name"}), name="medicine-price-info-search"),

] + router.urls
