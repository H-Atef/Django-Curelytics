from django.contrib import admin

from . import models

admin.site.register(models.DiseaseSymptom)
admin.site.register(models.ActvIngDisease)
admin.site.register(models.ActvIngredientsMedInfo)
