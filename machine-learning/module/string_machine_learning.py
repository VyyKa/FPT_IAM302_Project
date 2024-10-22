from gensim.models import FastText
from sklearn.linear_model import SGDClassifier
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.pipeline import Pipeline
from sklearn.utils.validation import check_is_fitted
from sklearn.metrics import classification_report
from sklearn.exceptions import NotFittedError
import numpy as np
import joblib

class StringMachineLearning:
    def __init__(self, labels: list, strings: list, debug: bool = False):
        self.__labels = labels
        self.__strings = strings
        self.debug = debug
        self.__classes = list(set(labels))  # Lưu lại danh sách các nhãn

        # Khởi tạo mô hình FastText và các mô hình học máy
        self.__parse_data()
        self.__init_models()

    def __parse_data(self):
        '''
        Parse strings thành list các từ.
        '''
        self.__tokenized_strings = self.__strings

    def __init_models(self):
        '''
        Khởi tạo FastText và các mô hình học máy.
        '''
        # Huấn luyện mô hình FastText trên dữ liệu
        self.fasttext_model = FastText(
            vector_size=100, window=3, min_count=1, epochs=10
        )

        # Gensim cần danh sách các câu (mỗi câu là một list từ) để huấn luyện
        self.fasttext_model.build_vocab(self.__tokenized_strings)
        self.fasttext_model.train(
            self.__tokenized_strings, total_examples=len(self.__tokenized_strings), epochs=10
        )

        # Khởi tạo các mô hình học máy
        self.sgd = SGDClassifier(max_iter=1000, tol=1e-3)
        self.rf = RandomForestClassifier()

        # Ensemble model kết hợp SGD và RandomForest
        self.ensemble = VotingClassifier(
            estimators=[('sgd', self.sgd), ('rf', self.rf)], voting='soft'
        )

    def __get_fasttext_vectors(self, strings: list) -> np.ndarray:
        '''
        Chuyển danh sách các chuỗi thành vector trung bình từ FastText.
        '''
        tokenized_data = strings
        vectors = [
            np.mean([self.fasttext_model.wv[word] for word in words if word in self.fasttext_model.wv] 
                    or [np.zeros(self.fasttext_model.vector_size)], axis=0)
            for words in tokenized_data
        ]
        return np.array(vectors)

    def train(self):
        '''
        Huấn luyện ban đầu trên toàn bộ dữ liệu.
        '''
        X = self.__get_fasttext_vectors(self.__strings)
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

        X_new = self.__get_fasttext_vectors(new_strings)

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

        X = self.__get_fasttext_vectors(input_strings)
        return self.ensemble.predict(X)

    def save_model(self, model_path: str):
        '''
        Lưu mô hình ra file.
        '''
        if model_path is None:
            raise ValueError("The model_path is None")
        joblib.dump((self.ensemble, self.fasttext_model), model_path)

    def load_model(self, model_path: str):
        '''
        Tải mô hình từ file.
        '''
        self.ensemble, self.fasttext_model = joblib.load(model_path)
