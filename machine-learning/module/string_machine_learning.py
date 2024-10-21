from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.pipeline import Pipeline
from sklearn.utils.validation import check_is_fitted
from sklearn.metrics import classification_report
from sklearn.exceptions import NotFittedError
import joblib

class StringMachineLearning:
    def __init__(self, labels: list, strings: list, debug: bool = False):
        self.__labels = labels
        self.__strings = strings
        self.debug = debug
        self.__classes = list(set(labels))  # Lưu lại danh sách các nhãn

        # Khởi tạo pipeline và các mô hình
        self.__init_models()
        self.__parse_data()

    def __parse_data(self):
        '''
        Parse strings thành list các từ để đưa vào vectorizer.
        '''
        self.__concatenated_strings = [" ".join(string) for string in self.__strings]

    def __init_models(self):
        '''
        Khởi tạo SGDClassifier và RandomForest trong ensemble.
        '''
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=5000)
        self.sgd = SGDClassifier(max_iter=1000, tol=1e-3)
        self.rf = RandomForestClassifier()

        # Ensemble model để kết hợp cả SGD và RandomForest
        self.ensemble = VotingClassifier(
            estimators=[('sgd', self.sgd), ('rf', self.rf)], voting='soft'
        )

    def train(self):
        '''
        Huấn luyện ban đầu trên toàn bộ dữ liệu.
        '''
        X = self.vectorizer.fit_transform(self.__concatenated_strings)
        y = self.__labels

        self.ensemble.fit(X, y)

        if self.debug:
            print("Initial training completed.")

    def update_model(self, new_strings: list, new_labels: list):
        '''
        Cập nhật mô hình với dữ liệu mới.
        '''
        try:
            check_is_fitted(self.ensemble)  # Kiểm tra mô hình đã huấn luyện chưa
        except NotFittedError:
            raise ValueError("Model is not initialized. Call train() first.")

        new_data = [" ".join(string) for string in new_strings]
        X_new = self.vectorizer.transform(new_data)

        # Cập nhật chỉ SGDClassifier (partial_fit)
        self.sgd.partial_fit(X_new, new_labels, classes=self.__classes)

        if self.debug:
            print("Model updated with new data.")

    def predict(self, input_strings: list) -> list:
        '''
        Dự đoán nhãn của các chuỗi đầu vào.
        '''
        if input_strings is None:
            raise ValueError("The input_strings is None")

        input_data = [" ".join(s) for s in input_strings]
        X = self.vectorizer.transform(input_data)
        return self.ensemble.predict(X)

    def save_model(self, model_path: str):
        '''
        Lưu mô hình ra file.
        '''
        if model_path is None:
            raise ValueError("The model_path is None")
        joblib.dump(self.ensemble, model_path)

    def load_model(self, model_path: str):
        '''
        Tải mô hình từ file.
        '''
        self.ensemble = joblib.load(model_path)
