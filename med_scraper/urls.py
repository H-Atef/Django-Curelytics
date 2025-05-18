from django.contrib import admin
from django.urls import path,include
from rest_framework.routers import DefaultRouter
from . import views

router=DefaultRouter()
router.register("medicine-info",views.MedicineViewSet,basename="medicine-info")

urlpatterns = [
    path("scrape/",views.MedicineViewSet.as_view({"get":"scrape_medicines","post":"scrape_medicines"}),name="scrape-medicines")
]+router.urls
