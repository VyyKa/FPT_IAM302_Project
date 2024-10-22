from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction import FeatureHasher
from sklearn.pipeline import Pipeline
from sklearn.linear_model import SGDClassifier
import joblib
import pandas as pd

from .machine_learning import MachineLearning

class BehaviorMachineLearning(MachineLearning):
    def __init__(self, labels: list, behaviors: dict, debug: bool = False):
        self.__labels = labels
        self.__behaviors = behaviors
        self.__pipeline = None
        self.debug = debug

        # Parse the data
        self.__df = self.__parse_data(behaviors)

    def __parse_data(self, behaviors: dict = None) -> pd.DataFrame:
        '''
        Parse the behaviors
        '''
        df = pd.DataFrame(behaviors)
        # Convert the list of strings to a single string by joining them
        df['api_text'] = df['resolved_apis'].apply(lambda x: ' '.join(x))
        df['command_text'] = df['executed_commands'].apply(lambda x: ' '.join(x))

        # Apply TF-IDF to the API and Command
        tfidf_api = TfidfVectorizer()
        tfidf_command = TfidfVectorizer()
        # Convert the API and Command to vectors
        api_features = tfidf_api.fit_transform(df["api_text"]).toarray()
        command_features = tfidf_command.fit_transform(df["command_text"]).toarray()
        # Create a DataFrame for the API and Command vectors
        api_df = pd.DataFrame(api_features, columns=[f'api_{i}' for i in range(api_features.shape[1])])
        command_df = pd.DataFrame(command_features, columns=[f'cmd_{i}' for i in range(command_features.shape[1])])

        # Combine the DataFrames
        df = pd.concat([df, api_df, command_df], axis=1)
        # Drop the unnecessary columns
        df.drop(["api_text", "command_text"], axis=1, inplace=True)
        df.drop(["resolved_apis", "executed_commands"], axis=1, inplace=True)

        # Apply Hashing Trick to the files and registry keys
        file_hasher = FeatureHasher(n_features=10, input_type='string')
        key_hasher = FeatureHasher(n_features=10, input_type='string')

        # Ensure 'files' and 'keys' columns are lists of lists of strings
        df['files'] = df['files'].apply(lambda x: x if isinstance(x, list) else [x])
        df['keys'] = df['keys'].apply(lambda x: x if isinstance(x, list) else [x])

        file_features = file_hasher.transform(df['files']).toarray()
        key_features = key_hasher.transform(df['keys']).toarray()

        # Convert to DataFrame and combine into the main DataFrame
        file_df = pd.DataFrame(file_features, columns=[f'file_{i}' for i in range(file_features.shape[1])])
        key_df = pd.DataFrame(key_features, columns=[f'key_{i}' for i in range(key_features.shape[1])])

        df = pd.concat([df, file_df, key_df], axis=1)
        df.drop(["files", "keys"], axis=1, inplace=True)
        df.drop(["read_files", "write_files", "read_keys", "write_keys", "delete_files", "delete_keys"], axis=1, inplace=True)

        # One-Hot Encoding for the started services
        df_services = pd.get_dummies(df['started_services'].apply(lambda x: ','.join(x) if x else 'none'))
        df_created_services = pd.get_dummies(df['created_services'].apply(lambda x: ','.join(x) if x else 'none'))
        df = pd.concat([df, df_services, df_created_services], axis=1)
        df.drop(["started_services"], axis=1, inplace=True)
        df.drop(["created_services"], axis=1, inplace=True)

        # mutexes
        df['mutexes'] = df['mutexes'].apply(lambda x: x if isinstance(x, list) else [x])
        df_mutexes = pd.get_dummies(df['mutexes'].apply(lambda x: ','.join(x) if x else 'none'))
        df = pd.concat([df, df_mutexes], axis=1)
        df.drop(["mutexes"], axis=1, inplace=True)

        df["label"] = self.__labels

        return df


    @property
    def labels(self) -> list:
        return self.__labels
    
    @property
    def behaviors(self) -> dict:
        return self.__behaviors
    
    def train(self):
        # Create a self.__pipeline
        self.__pipeline = Pipeline([
            ('clf', SGDClassifier(loss='log_loss', warm_start=True))
        ], memory=None)


        # Check to not split the data if the debug is True or the length of the data is < 5
        if self.debug or len(self.labels) < 5:
            x_train = self.__df.drop("label", axis=1)
            y_train = self.__df["label"]
            x_test = self.__df.drop("label", axis=1)
            y_test = self.__df["label"]
        else:
            # Split the data into training and testing
            x_train, x_test, y_train, y_test = train_test_split(
                self.__df.drop("label", axis=1), self.__df["label"], test_size=0.3
            )

        # Train the model with SGDClassifier
        self.__pipeline.named_steps['clf'].partial_fit(x_train, y_train, classes=[0, 1])

        # Predict the test data
        y_pred = self.__pipeline.predict(x_test)

        # Print the classification report
        if self.debug:
            print(classification_report(y_test, y_pred))

    def predict(self, behaviors: dict = None) -> list:
        '''
        Predict the labels of the behaviors
        '''
        if behaviors is None:
            raise ValueError("The behaviors is None")
        
        # Parse the behaviors
        df = self.__parse_data(behaviors)
        # Predict the labels
        return self.__pipeline.predict(df.drop("label", axis=1))
    
    def update_model(self, behaviors: dict, labels: list):
        '''
        Update the model with the new behaviors
        '''
        if behaviors is None:
            raise ValueError("The behaviors is None")
        if labels is None:
            raise ValueError("The labels is None")
        
        # Parse the behaviors
        df = self.__parse_data(behaviors)
        df["label"] = labels

        # Update the model
        self.__pipeline.named_steps['clf'].partial_fit(df.drop("label", axis=1), df["label"], classes=[0, 1])

    def save_model(self, model_path: str = None):
        '''
        Save the model to a file
        '''
        if model_path is None:
            raise ValueError("The model_path is None")
        joblib.dump(self.__pipeline, model_path)

    def load_model(self, model_path: str = None):
        '''
        Load the model from a file
        '''
        if model_path is None:
            raise ValueError("The model_path is None")
        self.__pipeline = joblib.load(model_path)