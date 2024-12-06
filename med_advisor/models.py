from django.db import models

class DiseaseSymptom(models.Model):
    disease=models.CharField(max_length=250,default="-") 
    symptom=models.CharField(max_length=250,default="-") 
    disease_class=models.CharField(max_length=550,default="-") 


    class Meta:
        verbose_name = "Disease"
        verbose_name_plural = "Diseases"
        
class ActvIngDisease(models.Model):
    primary_treatment=models.CharField(max_length=250,default="-") 
    alt_treatment_one=models.CharField(max_length=250,default="-") 
    alt_treatment_two=models.CharField(max_length=250,default="-") 
    disease=models.CharField(max_length=250,default="-") 
    


    class Meta:
        verbose_name = "Treament Active Ing."
        verbose_name_plural = "Treaments Active Ing."

