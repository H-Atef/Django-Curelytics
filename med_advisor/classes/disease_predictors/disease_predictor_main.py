import importlib
from typing import Dict, Any, List, Tuple
from med_advisor.classes.disease_predictors.base_disease_predictor import DiseasePredictor  # Keep this import for the base class

path_d='med_advisor.classes.disease_predictors.'



class MedDataContext:
    """
    Context class to manage different disease prediction strategies (predictors).
    """

    def __init__(self):
        """
        Initializes the context with a dictionary that maps each predictor to their corresponding module and class.
        """
        # Dictionary to map predictor names to their corresponding module path and class name
        self.predictor_map: Dict[str, str] = {
            'custom': f'{path_d}custom_disease_predictor.CustomDiseasePredictor',
            'groq': f'{path_d}groq_disease_predictor.GroqDiseasePredictor'
        }
        self.current_predictor: DiseasePredictor = None

    def set_predictor(self, predictor_name: str, **kwargs: Any) -> None:
        """
        Set the current predictor strategy based on the name provided.
        
        Args:
            predictor_name: The name of the predictor strategy (e.g., 'custom', 'groq').
            kwargs: Additional parameters required to initialize the predictor.
        """
        if predictor_name in self.predictor_map:
            # Dynamically import the predictor class using importlib
            module_path, class_name = self.predictor_map[predictor_name].rsplit('.', 1)
            
            # Import the module
            module = importlib.import_module(module_path)
            
            # Get the class from the module
            predictor_class = getattr(module, class_name)
            
            # Instantiate the chosen predictor with the provided arguments
            self.current_predictor = predictor_class(**kwargs)
            print(f"Switched to {predictor_name} predictor.")
        else:
            raise ValueError(f"Predictor {predictor_name} not found in the available strategies.")

    def predict(self, symptoms_list: list, **kwargs: Any) -> List[List[Tuple[str, str]]]:
        """
        Makes predictions using the current selected predictor.
        
        Args:
            symptoms_list: A list of symptoms (strings) for which predictions are needed.
            top_n: The number of top predictions to return (default is 3).
        
        Returns:
            The predictions made by the current predictor.
        """
        if self.current_predictor:
            return self.current_predictor.predict(symptoms_list, **kwargs)
        else:
            raise RuntimeError("No predictor has been selected. Use set_predictor first.")
