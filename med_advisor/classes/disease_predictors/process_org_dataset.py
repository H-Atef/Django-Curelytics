import pandas as pd
from sklearn.utils import resample
import importlib
from pathlib import Path


PATH="./med_advisor/classes/disease_predictors"

MODULE="med_advisor.classes.disease_predictors.common_diseases_list"

cd=importlib.import_module(MODULE)


class OriginalDatasetPre:

    def __init__(self, df: pd.DataFrame= pd.read_csv(f'{PATH}/datasets/disease_symptom_dataset.csv')):
        self.df = df
        self.disease_classes = cd.disease_classes

        

    def map_disease_to_class(self):
        # Create a reverse mapping from disease to class for faster lookup
        disease_to_class = {disease.lower().strip(): cls for cls, diseases in self.disease_classes.items() for disease in diseases}

        # Map each disease in the 'Disease' column to its corresponding class
        self.df['Disease_Class'] = self.df['Disease'].map(lambda x: disease_to_class.get(x.strip().lower(), 'Unknown'))

        return self.df



    def fill_and_group_symptoms(self) -> pd.DataFrame:
        try:
            # Fill NaN values with empty string
            self.df = self.df.fillna("")

            # Dynamically select symptom columns (assuming symptom columns have a consistent naming convention)
            symptom_columns = [col for col in self.df.columns if col.startswith('Symptom_')]

            # Remove extra spaces in between (in case some symptom columns are empty)
            self.df["Symptoms"] = self.df[symptom_columns].apply(lambda row: " ".join(filter(bool, row)), axis=1)

            # Drop the individual symptom columns
            self.df.drop(symptom_columns, axis=1, inplace=True)

            return self.df

        except Exception as e:
            print(e)
            return pd.DataFrame({})

    def balance_dataset(self) -> pd.DataFrame:
        try:
            # Get the value counts of the Disease_Class column
            class_counts = self.df['Disease_Class'].value_counts()

            # Find the maximum class size (to balance all other classes)
            max_class_size = class_counts.max()

            # Create lists of classes that need to be oversampled (those with fewer rows than the maximum)
            oversample_classes = [cls for cls, count in class_counts.items() if count < max_class_size]
            undersample_classes = [cls for cls, count in class_counts.items() if count > max_class_size]

            # Perform Oversampling for underrepresented classes
            oversampled_data = []
            for cls in oversample_classes:
                class_data = self.df[self.df['Disease_Class'] == cls]
                oversampled_data.append(resample(class_data, 
                                                 replace=True,  # With replacement
                                                 n_samples=max_class_size - len(class_data),  # Number of samples to add
                                                 random_state=42))  # For reproducibility

            # Perform Undersampling for overrepresented classes
            undersampled_data = []
            for cls in undersample_classes:
                class_data = self.df[self.df['Disease_Class'] == cls]
                undersampled_data.append(resample(class_data, 
                                                  replace=False,  # Without replacement
                                                  n_samples=max_class_size,  # Limit to the maximum size
                                                  random_state=42))  # For reproducibility

            # Concatenate all resampled datasets
            balanced_data = pd.concat([self.df] + oversampled_data + undersampled_data)

            # Shuffle the dataset after resampling (optional but recommended)
            balanced_data = balanced_data.sample(frac=1, random_state=42).reset_index(drop=True)

            self.df = balanced_data.copy()

            return self.df

        except Exception as e:
            print(e)
            return pd.DataFrame({})

    def process_dataset(self, new_diseases_list=None) -> pd.DataFrame:
        try:
           
           
           
           if Path(f"{PATH}/datasets/processed_dataset.csv").is_file():
               processed_df=pd.read_csv(f"{PATH}/datasets/processed_dataset.csv")

               self.df=processed_df.copy()

               return self.df
                
                
           else:
                self.fill_and_group_symptoms()
                self.map_disease_to_class()  # Ensure Disease_Class is assigned
                self.balance_dataset()
            

                # Save the processed dataset
                self.df.to_csv(f"{PATH}/datasets/processed_dataset.csv", index=False)

                return self.df

        except Exception as e:
            print(e)
            return pd.DataFrame({})


# Example usage:

# if __name__=="__main__":

#     # Load the initial dataset
#     df = pd.read_csv('./datasets/disease_symptom_dataset.csv')


#     # Create an instance of the OriginalDatasetPre class
#     pre = OriginalDatasetPre(df)

   
#     df = pre.process_dataset()

    # # Output the balanced dataset
    # print(df["Disease_Class"].value_counts())
