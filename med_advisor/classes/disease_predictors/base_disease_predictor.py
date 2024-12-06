from abc import ABC,abstractmethod
from typing import List,Type,Any,Tuple
from sklearn.base import ClassifierMixin

class DiseasePredictor(ABC):
    """
    Abstract Base Class for a disease prediction model.
    It provides common methods for model initialization, saving, loading, and prediction.
    """

    def __init__(self, df: Any, model: Type[ClassifierMixin], model_params: dict = None, max_features: int = 5000):
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
        self.max_features = max_features

    @abstractmethod
    def initialize_model(self) -> dict:
        """
        Abstract method to initialize and train the machine learning model using the input dataframe.
        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def save_model(self, model_path: str, vectorizer_path: str, encoder_path: str) -> None:
        """
        Abstract method to save the trained model, vectorizer, and encoder to disk.
        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def load_model(self, model_path: str, vectorizer_path: str, encoder_path: str) -> None:
        """
        Abstract method to load the trained model, vectorizer, and encoder from disk.
        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def predict(self, input_list: List[str]) -> List[List[Tuple[str, str]]]:
        """
        Abstract method to make predictions on a list of input symptoms.
        Must be implemented by subclasses.
        """
        pass