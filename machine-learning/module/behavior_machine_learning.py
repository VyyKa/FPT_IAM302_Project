from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction import FeatureHasher
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
        df = pd.DataFrame(self.__behaviors)
        # Xử lý các chuỗi văn bản (API và Command) bằng cách nối lại
        df['api_text'] = df['resolved_apis'].apply(lambda x: ' '.join(x))
        df['command_text'] = df['executed_commands'].apply(lambda x: ' '.join(x))
        # Print the DataFrame
        # print(df["resolved_apis"])

        # Áp dụng TF-IDF cho API và Command
        tfidf_api = TfidfVectorizer()  # Giới hạn số lượng đặc trưng
        tfidf_command = TfidfVectorizer()
        # Chuyển đổi API và Command thành vector
        api_features = tfidf_api.fit_transform(df["api_text"]).toarray()
        command_features = tfidf_command.fit_transform(df["command_text"]).toarray()
        # Tạo DataFrame cho các vector API và Command
        api_df = pd.DataFrame(api_features, columns=[f'api_{i}' for i in range(api_features.shape[1])])
        command_df = pd.DataFrame(command_features, columns=[f'cmd_{i}' for i in range(command_features.shape[1])])
        # Kết hợp các DataFrame
        df = pd.concat([df, api_df, command_df], axis=1)
        # Xóa các cột không cần thiết
        df.drop(["api_text", "command_text"], axis=1, inplace=True)
        df.drop(["resolved_apis", "executed_commands"], axis=1, inplace=True)

        # print(api_features)
        # print(command_features)

        # Áp dụng Hashing Trick cho file và registry keys
        file_hasher = FeatureHasher(n_features=10, input_type='string')
        key_hasher = FeatureHasher(n_features=10, input_type='string')

        # Ensure 'files' and 'keys' columns are lists of lists of strings
        df['files'] = df['files'].apply(lambda x: x if isinstance(x, list) else [x])
        df['keys'] = df['keys'].apply(lambda x: x if isinstance(x, list) else [x])

        file_features = file_hasher.transform(df['files']).toarray()
        key_features = key_hasher.transform(df['keys']).toarray()

        # Chuyển thành DataFrame và kết hợp vào DataFrame chính
        file_df = pd.DataFrame(file_features, columns=[f'file_{i}' for i in range(file_features.shape[1])])
        key_df = pd.DataFrame(key_features, columns=[f'key_{i}' for i in range(key_features.shape[1])])

        df = pd.concat([df, file_df, key_df], axis=1)
        df.drop(["files", "keys"], axis=1, inplace=True)
        df.drop(["read_files", "write_files", "read_keys", "write_keys", "delete_files", "delete_keys"], axis=1, inplace=True)

        # Print
        print("File Features", file_features)
        print("Key Features", key_features)

        # # One-Hot Encoding cho các dịch vụ được khởi chạy
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

        print(df)
        # Export the data to a CSV file
        df.to_csv("data.csv", index=False)
        print(self.labels)
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