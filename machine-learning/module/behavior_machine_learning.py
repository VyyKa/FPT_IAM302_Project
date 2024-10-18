from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.pipeline import Pipeline
import joblib
import pandas as pd

class BehaviorMachineLearning:
    def __init__(self, labels: list, behaviors: dict, debug: bool = False):
        self.__labels = labels
        self.__behaviors = behaviors
        self.__pipeline = None
        self.debug = debug

    @property
    def labels(self) -> list:
        return self.__labels
    
    @property
    def behaviors(self) -> dict:
        return self.__behaviors
    
    def train(self):
        # Create a DataFrame from the behaviors
        df = pd.DataFrame(self.behaviors).T
        df["label"] = self.labels

        # Create a self.__pipeline
        self.__pipeline = Pipeline(
            [
                ("clf", RandomForestClassifier()),
            ],
            memory=None  # Specify a memory argument
        )

        # Check to not split the data if the debug is True or the length of the data is < 5
        if self.debug or len(self.labels) < 5:
            x_train = df.drop("label", axis=1)
            y_train = df["label"]
            x_test = df.drop("label", axis=1)
            y_test = df["label"]
        else:
            # Split the data into training and testing
            x_train, x_test, y_train, y_test = train_test_split(
                df.drop("label", axis=1), df["label"], test_size=0.3
            )

        # Train the model
        self.__pipeline.fit(x_train, y_train)

        # Predict the test data
        y_pred = self.__pipeline.predict(x_test)

        # Print the classification report
        if self.debug:
            print(classification_report(y_test, y_pred))

    def predict(self, behaviors: dict) -> list:
        '''
        Predict the labels of the behaviors
        '''
        # Create a DataFrame from the behaviors
        df = pd.DataFrame(behaviors).T

        # Predict the labels
        return self.__pipeline.predict(df)
    
    def save_model(self, model_path: str):
        '''
        Save the model to a file
        '''
        joblib.dump(self.__pipeline, model_path)