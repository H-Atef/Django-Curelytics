from django.db import models

class MedicinePriceInfo(models.Model):
    drug_name=models.CharField(max_length=250,default="-") 
    price=models.CharField(max_length=250,default="-") 
    repeat=models.CharField(max_length=250,default="-") 
    search_q=models.CharField(max_length=250,default="-") 

    class Meta:
        verbose_name = "Medicine Price"
        verbose_name_plural = "Medicines Prices"
