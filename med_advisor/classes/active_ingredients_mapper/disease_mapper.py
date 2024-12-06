
import pandas as pd
from typing import List,Tuple,Dict
from fuzzywuzzy import fuzz
import importlib

from med_advisor import models,serializers

module1='med_advisor.classes.active_ingredients_mapper.dataset_generator.active_ingredients_list'
module2='med_advisor.classes.active_ingredients_mapper.ai_mapper'
path_actv="./med_advisor/classes/active_ingredients_mapper"

actv=importlib.import_module(module1)
actv_ai=importlib.import_module(module2)

class DiseaseActvIngMapper:

    def __init__(self,
                 predicted_diseases:List[List[Tuple[str,str]]]=None
                 ):
        
        # Retrieve all actvIng-disease records from the database
        actvIng_disease_data = models.ActvIngDisease.objects.all()
        serializer = serializers.ActvIngDiseaseSerializer(actvIng_disease_data, many=True)
        
        if serializer.data!=[]:
            df=pd.DataFrame(serializer.data)
            df.columns=['Primary Active Ingredient','Alternative Treatment 1','Alternative Treatment 2','Diseases']
        else:
            df=pd.read_csv(f"{path_actv}/datasets/active_ingredients_diseases.csv")

        self.df=df
        self.predicted_diseases=predicted_diseases
        

    
    def extract_diseases_only(self,predicted_diseases:List[List[Tuple[str,str]]]=None)->List:

        if type(predicted_diseases[0])==str or predicted_diseases==[]:
            return predicted_diseases

        
        #Extracting diseases Only from the input using list comperhension
        extarcted_diseases_list=[disease[0] for tuple in predicted_diseases for disease in tuple]

        return extarcted_diseases_list
    

    def check_and_filter_new_diseases(self,diseases_list:List[str]=None)->List:
        lower_case_disease_classes=[x.lower() for x in actv.diseases_cls_to_active_ingredients.keys()]
        

        filtered_list=[disease for disease in diseases_list if
                        (not disease.strip(" ").lower() in lower_case_disease_classes) and
                        (not disease.strip(" ").lower() in list(self.df["Diseases"].str.lower()))
                        ]
        
        return filtered_list


    def map_pridected_diseases_to_actv(self,predicted_diseases:List[List[Tuple[str,str]]]=None)->Dict:

        if predicted_diseases is None:
            if not self.predicted_diseases is None:
                predicted_diseases=self.predicted_diseases
            
            else:
                return {}
            
        
        extarcted_diseases_list=self.extract_diseases_only(predicted_diseases)

       
                
        #The final output dictionary that includes all mapped diseases
        active_ingredients_output_dict={}



        #A loop for mapping extracted diseases with their active ingredients
        for disease in extarcted_diseases_list:
            
            self.map_diseases_cls(disease,active_ingredients_output_dict)

            self.map_diseases(disease,active_ingredients_output_dict)


        filtered_list=self.check_and_filter_new_diseases(extarcted_diseases_list)


        if filtered_list !=[]:
            new_diseses_dict=self.ai_map_disease_to_actv_ing(filtered_list)

            if not new_diseses_dict=={}:
                active_ingredients_output_dict.update(new_diseses_dict)
                self.save_new_disease_records(new_diseses_dict)
            

        return active_ingredients_output_dict


    def map_diseases_cls(self,disease:str,actv_ing_output:Dict)->Dict:

        lower_case_disease_classes=[x.lower() for x in actv.diseases_cls_to_active_ingredients.keys()]

        if disease.lower() in lower_case_disease_classes:
            actv_ing_output[disease.split("(")[0].strip(" ")]=actv.diseases_cls_to_active_ingredients[disease]
        
        return actv_ing_output
        
    def is_similar(treatment1: str, treatment2: str, threshold=90) -> bool:
        return fuzz.ratio(treatment1.lower(), treatment2.lower()) >= threshold
         


    def map_diseases(self,disease:str,actv_ing_output:Dict)->Dict:

        lower_case_disease_classes=[x.lower() for x in actv.diseases_cls_to_active_ingredients.keys()]

        if (disease.strip(" ").lower() in list(self.df["Diseases"].str.lower()) ) and (not disease.strip(" ").lower() in lower_case_disease_classes):
                
                row=self.df[self.df["Diseases"].str.lower()==disease.lower().strip(" ")]
                row=row.to_dict(orient="list")

                # Extract the treatments: Primary, Alternative 1, and Alternative 2
                treatments = row['Primary Active Ingredient'] + \
                            row['Alternative Treatment 1'] + \
                            row['Alternative Treatment 2']
                
                # Remove duplicates by converting to a set, then back to a list
                unique_treatments = list(set(treatments))

              

                actv_ing_output[disease]=unique_treatments

        return actv_ing_output
    
    def save_new_disease_records(self,data_dict:Dict=None)->pd.DataFrame:

        try:

            new_df = pd.DataFrame.from_dict(
                            {disease: {
                                'Primary Active Ingredient': ingredients[0] if len(ingredients) > 0 else None,
                                'Alternative Treatment 1': ingredients[1] if len(ingredients) > 1 else None,
                                'Alternative Treatment 2': ingredients[2] if len(ingredients) > 2 else None,
                                'Diseases': disease
                            } for disease, ingredients in data_dict.items()},
                            orient='index'
                        ).reset_index(drop=False)

            try:
                ai_df = pd.read_csv(f"{path_actv}/datasets/ai_active_ingredients_diseases.csv")
            except FileNotFoundError:
                # If file is not found, create an empty DataFrame with the specified columns
                ai_df = pd.DataFrame(columns=[
                    'Primary Active Ingredient','Alternative Treatment 1', 
                    'Alternative Treatment 2', 'Diseases'])

            # Append the new data to the existing DataFrame
            self.df = pd.concat([self.df, new_df], ignore_index=True)
            ai_df = pd.concat([ai_df, new_df], ignore_index=True)

            self.df.drop('index',axis=1,inplace=True)
            ai_df.drop('index',axis=1,inplace=True)

            self.df.copy().to_csv(f"{path_actv}/datasets/active_ingredients_diseases.csv",index=False)
            ai_df.to_csv(f"{path_actv}/datasets/ai_active_ingredients_diseases.csv",index=False)

            # Append the new data to DB
            instances = []
            new_df.drop('index',axis=1,inplace=True)
            new_df.columns=["primary_treatment", "alt_treatment_one","alt_treatment_two","disease"]
           
            for index, row in new_df.iterrows():
                actv = row.to_dict()
                instance = models.ActvIngDisease(**actv)
                instances.append(instance)

            # Save the data to the database in bulk
            models.ActvIngDisease.objects.bulk_create(instances)


        except Exception as e:
            print(e)


    def ai_map_disease_to_actv_ing(self,diseases:List)->Dict:
        groq_mapper=actv_ai.GroqActvIngMapper()
        result=groq_mapper.map_diseases(diseases_list=diseases)
        return result



# output_example= [[('Gastrointestinal Disorders (Diarrhea, Gastroenteritis, Stomach Ulcer, Peptic Ulcer Disease, GERD)', '53.00%'),
#                   ('Respiratory Diseases (Asthma, COPD, Pneumonia, Bronchitis, COVID)', '20.00%'), 
#                   ('Skin Disorders (Acne, Psoriasis, Impetigo, Fungal Infections)', '11.00%'),
#                   ("common cold","10%")
#                   ]]

# actv_mapper=DiseaseActvIngMapper()

# print(actv_mapper.map_pridected_diseases_to_actv(output_example))



