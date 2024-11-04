from django.db import models

class MedicineInfo(models.Model):
  drug_name=models.CharField(max_length=250,default="-") 
  generic_name=models.CharField(max_length=250,default="-") 
  drug_class=models.CharField(max_length=250,default="-") 
  similars=models.CharField(max_length=250,default="-") 
  alternatives=models.CharField(max_length=250,default="-") 
  
  class Meta:
    verbose_name = "Medicine"
    verbose_name_plural = "Medicines"