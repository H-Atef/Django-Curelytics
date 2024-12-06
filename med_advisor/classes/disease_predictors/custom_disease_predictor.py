from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier



from typing import Type, Any, List,Tuple
import os
import pickle
import pandas as pd
import numpy as np

import importlib

module1='med_advisor.classes.disease_predictors.base_disease_predictor'
path="./med_advisor/classes/disease_predictors"



class CustomDiseasePredictor(importlib.import_module(module1).DiseasePredictor):

    def __init__(self, df: Any= pd.read_csv(f'{path}/datasets/processed_dataset.csv') , model: Type[Any] = RandomForestClassifier, model_params: dict = None):
        """
        Initializes the model with the dataframe and the type of machine learning model.
        Args:
            df: The input DataFrame containing 'Symptoms' and 'Disease' columns.
            model: The machine learning model class (e.g., RandomForestClassifier, SVC).
            model_params: A dictionary of hyperparameters for the model.
            max_features: The maximum number of features for the TF-IDF vectorizer.
        """
        self.df = df
        self.model = None
        self.vectorizer = None
        self.label_encoder = None
        self.model_class = model
        self.model_params = model_params if model_params else {}


    def initialize_model(self) -> dict:
        """
        Initializes and trains the machine learning model using the input dataframe.
        Returns:
            A dictionary containing the trained model, accuracy score, and classification report.
        """
        try:
            # Ensure the necessary columns are present
            if 'Symptoms' not in self.df or 'Disease_Class' not in self.df:
                raise ValueError("Input DataFrame must contain 'Symptoms' and 'Disease' columns.")

            # Step 1: Extract features and target
            X = self.df['Symptoms']
            y = self.df['Disease_Class']

            # Step 2: Vectorize the symptoms using TF-IDF
            vectorizer = TfidfVectorizer()
            X_tfidf = vectorizer.fit_transform(X)

            # Step 3: Encode the target labels (diseases) into numerical values
            label_encoder = LabelEncoder()
            y_encoded = label_encoder.fit_transform(y)

            # Step 4: Split the data into training and testing sets
            X_train, X_test, y_train, y_test = train_test_split(X_tfidf, y_encoded, test_size=0.20, random_state=44,shuffle=True)

            # Step 5: Initialize and train the model with provided parameters
            model = self.model_class(**self.model_params)
            model.fit(X_train, y_train)

            # Step 6: Make predictions and evaluate the model
            y_pred = model.predict(X_test)
            acc_score = accuracy_score(y_test, y_pred)
            cls_report = classification_report(y_test, y_pred, target_names=label_encoder.classes_)

            # Store the trained components
            self.model = model
            self.vectorizer = vectorizer
            self.label_encoder = label_encoder

            return {
                "model": model,
                "accuracy_score": acc_score,
                "classification_report": cls_report
            }

        except Exception as e:
            print(f"An error occurred during model initialization: {e}")
            return {"error": str(e)}


    def save_model(self, model_path: str = f'{path}/custom_model/model.pkl', 
                   vectorizer_path: str = f'{path}/custom_model/vectorizer.pkl', 
                   encoder_path: str = f'{path}/custom_model/label_encoder.pkl') -> None:
        """
        Saves the trained model, vectorizer, and encoder to disk with default filenames.
        Args:
            model_path: Path to save the trained model.
            vectorizer_path: Path to save the TF-IDF vectorizer.
            encoder_path: Path to save the label encoder.
        """
        try:
            # Ensure the model, vectorizer, and encoder are trained
            if not self.model or not self.vectorizer or not self.label_encoder:
                raise RuntimeError("Model, vectorizer, or label encoder is not trained.")
            
            if not os.path.exists(f"{path}/custom_model/"):
                os.makedirs(f"{path}/custom_model/") 

            # Save the Random Forest model
            with open(model_path, 'wb') as model_file:
                pickle.dump(self.model, model_file)

            # Save the TF-IDF vectorizer
            with open(vectorizer_path, 'wb') as vectorizer_file:
                pickle.dump(self.vectorizer, vectorizer_file)

            # Save the LabelEncoder
            with open(encoder_path, 'wb') as encoder_file:
                pickle.dump(self.label_encoder, encoder_file)

            print("Model, vectorizer, and encoder saved successfully!")
        
        except Exception as e:
            print(f"An error occurred while saving the model: {e}")

    def load_model(self, model_path: str = f'{path}/custom_model/model.pkl', 
                   vectorizer_path: str = f'{path}/custom_model/vectorizer.pkl', 
                   encoder_path: str = f'{path}/custom_model/label_encoder.pkl') -> None:
        """
        Loads the trained model, vectorizer, and encoder from disk with default filenames.
        Args:
            model_path: Path to the saved model file.
            vectorizer_path: Path to the saved vectorizer file.
            encoder_path: Path to the saved label encoder file.
        """
        try:

            if not os.path.exists(model_path) or not os.path.exists(vectorizer_path) or not os.path.exists(encoder_path):
                print("Model, vectorizer, or encoder not found. Initializing and training the model...")
                
                # Initialize and train the model since the files don't exist
                initialization_result = self.initialize_model()
                
                # If initialization is successful, save the model, vectorizer, and encoder
                if 'error' not in initialization_result:
                    self.save_model()
                    print("Model, vectorizer, and encoder saved successfully after initialization.")
                else:
                    print(f"Error during model initialization: {initialization_result['error']}")
                    return
                
            else:

                # Load the Random Forest model
                with open(model_path, 'rb') as model_file:
                    self.model = pickle.load(model_file)

                # Load the TF-IDF vectorizer
                with open(vectorizer_path, 'rb') as vectorizer_file:
                    self.vectorizer = pickle.load(vectorizer_file)

                # Load the LabelEncoder
                with open(encoder_path, 'rb') as encoder_file:
                    self.label_encoder = pickle.load(encoder_file)

        except Exception as e:
            print(f"An error occurred while loading the model: {e}")

    
    def predict(self, input_list: List[str], top_n: int = 3) -> List[List[Tuple[str, str]]]:
        """
        Predicts the top N diseases for a list of input symptoms.
        Args:
            input_list: A list of symptoms (strings) for which predictions need to be made.
            top_n: The number of top predictions to return (default is 5).
        Returns:
            A list of top N predicted disease names.
        """
        try:

            self.load_model()

            # Ensure that the model, vectorizer, and label encoder are loaded
            if not self.model or not self.vectorizer or not self.label_encoder:
                raise RuntimeError("Model, vectorizer, or label encoder is not loaded.")
            
            

            # Transform the new data using the loaded vectorizer
            new_data_tfidf = self.vectorizer.transform(input_list)

            # Get the probabilities for each class
            class_probabilities = self.model.predict_proba(new_data_tfidf)

            # Get the top N predictions for each input
            top_predictions = []
            for prob in class_probabilities:
                # Get the indices of the top N classes based on probability
                top_n_indices = np.argsort(prob)[-top_n:][::-1]
                 # Get the corresponding classes (disease names) for these indices
                top_n_classes = self.label_encoder.inverse_transform(top_n_indices)

                # Get the probabilities of the top N classes and convert to percentages
                top_n_probabilities = prob[top_n_indices] * 100

                # Format the predictions with their probabilities as percentages
                top_n_with_probabilities = [
                    (disease, f"{probability:.2f}%") for disease, probability in zip(top_n_classes, top_n_probabilities)
                ]
                
                # Append the formatted predictions for this input
                top_predictions.append(top_n_with_probabilities)


            return top_predictions

        except Exception as e:
            print(f"An error occurred during prediction: {e}")
            return {"error": str(e)}
        

# model = CustomDiseasePredictor()


# symptoms = ["Patient 1: A 35-year-old male presenting with a persistent dry cough, shortness of breath, chest tightness, and fever for the past 4 days. No prior history of asthma or allergies."]



# print(model.predict(symptoms))