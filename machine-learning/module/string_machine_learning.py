from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.pipeline import Pipeline
import joblib

class StringMachineLearning:
    def __init__(self, labels: list, strings: list, debug: bool = False):
        self.__labels = labels
        self.__strings = strings
        self.__pipeline = None
        self.debug = debug

    @property
    def labels(self) -> list:
        return self.__labels

    @property
    def strings(self) -> list:
        return self.__strings

    def train(self):
        # Concatenate all the strings into one string
        concatenated_strings = [" ".join(string) for string in self.strings]

        # Create a self.__pipeline
        self.__pipeline = Pipeline(
            [
                ("tfidf", TfidfVectorizer()),
                ("clf", RandomForestClassifier()),
            ],
            memory=None  # Specify a memory argument
        )

        # Split the data
        x_train, x_test, y_train, y_test = train_test_split(
            concatenated_strings, self.labels, test_size=0.2, random_state=42
        )

        # Train the model
        self.__pipeline.fit(x_train, y_train)

        # Predict the test data
        y_pred = self.__pipeline.predict(x_test)

        # Print the classification report
        if self.debug:
            print(classification_report(y_test, y_pred))

    def predict(self, strings: list) -> list:
        '''
        Predict the labels of the strings
        '''
        return self.__pipeline.predict(strings)

    def save_model(self, model_path: str) -> None:
        '''
        Save the model to a file
        '''
        joblib.dump(self.__pipeline, model_path)

    def load_model(self, model_path: str) -> None:
        '''
        Load the model from a file
        '''
        self.__pipeline = joblib.load(model_path)