import pandas as pd
import os
import importlib

MODULE="med_advisor.classes.active_ingredients_mapper.dataset_generator.active_ingredients_list"
PATH="med_advisor/classes/active_ingredients_mapper/"
ac=importlib.import_module(MODULE)

class ActiveIngredientsDatasetGenerator:

    @classmethod
    def generate_csv_file(cls) -> pd.DataFrame:
        try:
            # Create a list to store the final structured data
            final_data = []

            # Process each entry in the active ingredients list
            for entry in ac.active_ingredients_list:
                primary_treatment = entry[0]
                alternative_treatment_1 = entry[1] if len(entry) > 1 else None
                alternative_treatment_2 = entry[2] if len(entry) > 2 else None
                diseases = entry[3:]

                # If we don't have enough alternatives, fill with '-'
                alternative_treatment_1 = alternative_treatment_1 if alternative_treatment_1 else '-'
                alternative_treatment_2 = alternative_treatment_2 if alternative_treatment_2 else '-'

                # Append the structured data
                final_data.append([primary_treatment, alternative_treatment_1, alternative_treatment_2, ', '.join(diseases)])

            # Create DataFrame from the final data with descriptive column names
            df = pd.DataFrame(final_data, columns=['Primary Active Ingredient', 
                                                   'Alternative Treatment 1', 
                                                   'Alternative Treatment 2', 
                                                   'Diseases'])
            

            if not os.path.exists(f"{PATH}datasets/"):
                os.makedirs(f"{PATH}datasets/") 

            # Save the DataFrame to a CSV file
            df.to_csv(f'{PATH}datasets/active_ingredients_diseases.csv', index=False)

            return df
        
        except Exception as e:
            print(e)
            return pd.DataFrame({})

# # Generate the CSV file
# ActiveIngredientsDatasetGenerator.generate_csv_file()
