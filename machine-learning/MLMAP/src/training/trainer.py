import os
import joblib
import pandas as pd
import numpy as np
import hashlib

from keras.src.callbacks import EarlyStopping
from keras.src.layers import BatchNormalization
from keras.src.utils import pad_sequences
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, accuracy_score
from tensorflow.keras import Input
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Dropout, LSTM

class ModelTrainer:
    def __init__(self, file_path):
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
        self.file_path = os.path.join(os.path.dirname(__file__), file_path)
        self.data = pd.read_csv(self.file_path)

        self.columns_to_drop = ['label', 'filename']
        self.features = self.data.drop(columns=self.columns_to_drop, errors='ignore')
        self.labels = self.data['label']

        self.X_train, self.X_test, self.y_train, self.y_test = self._split_data()
        self.data_fingerprint = self._generate_data_fingerprint()

    def _split_data(self):
        return train_test_split(self.features, self.labels, test_size=0.2, random_state=42)

    def _generate_data_fingerprint(self):
        """Tạo một dấu vân tay (fingerprint) từ dữ liệu hiện tại để so sánh."""
        data_str = pd.util.hash_pandas_object(self.features).sum()
        return hashlib.md5(str(data_str).encode()).hexdigest()

    def _is_data_new(self, model_path, fingerprint_path):
        """Kiểm tra nếu dữ liệu hiện tại đã được mô hình xử lý chưa dựa trên fingerprint."""
        if os.path.exists(model_path) and os.path.exists(fingerprint_path):
            with open(fingerprint_path, 'r') as f:
                saved_fingerprint = f.read()
            if saved_fingerprint == self.data_fingerprint:
                return False  # Dữ liệu không thay đổi
        return True  # Có dữ liệu mới

    def _save_data_fingerprint(self, fingerprint_path):
        with open(fingerprint_path, 'w') as f:
            f.write(self.data_fingerprint)

    @staticmethod
    def _calculate_checksum(model_path):
        """Tính toán checksum MD5 của mô hình."""
        with open(model_path, 'rb') as f:
            model_data = f.read()
        return hashlib.md5(model_data).hexdigest()

    @staticmethod
    def save_model_checksums(rf_checksum, xgb_checksum, lstm_checksum):
        """Ghi các checksum của các mô hình vào file."""
        checksums_path = '../../models/stored/model_checksums.txt'
        with open(checksums_path, 'w') as f:
            f.write(f"Random Forest Checksum: {rf_checksum}\n")
            f.write(f"XGBoost Checksum: {xgb_checksum}\n")
            f.write(f"LSTM Checksum: {lstm_checksum}\n")

    def train_random_forest(self):
        model_path = '../../models/stored/rf_model.pkl'
        fingerprint_path = '../../models/stored/rf_model_fingerprint.txt'

        if not self._is_data_new(model_path, fingerprint_path):
            print("Random Forest: No new data to add! Loading existing model results...")
            rf_model = self.load_random_forest()
            rf_predictions = rf_model.predict(self.X_test)
            rf_accuracy = accuracy_score(self.y_test, rf_predictions)
            rf_classification_report = classification_report(self.y_test, rf_predictions, zero_division=1)
            rf_probabilities = rf_model.predict_proba(self.X_test)[:, 1]  # Lấy xác suất lớp dương (1)

            rf_checksum = self._calculate_checksum(model_path)
            return rf_accuracy, rf_classification_report, rf_probabilities.tolist(), rf_checksum

        print("Training Random Forest with new data...")
        rf_model = RandomForestClassifier(random_state=42)
        rf_model.fit(self.X_train, self.y_train)

        rf_predictions = rf_model.predict(self.X_test)
        rf_accuracy = accuracy_score(self.y_test, rf_predictions)
        rf_classification_report = classification_report(self.y_test, rf_predictions, zero_division=1)
        rf_probabilities = rf_model.predict_proba(self.X_test)[:, 1]

        # Save model and data fingerprint
        joblib.dump(rf_model, model_path)
        self._save_data_fingerprint(fingerprint_path)

        rf_checksum = self._calculate_checksum(model_path)
        return rf_accuracy, rf_classification_report, rf_probabilities.tolist(), rf_checksum

    def train_xgboost(self):
        model_path = '../../models/stored/xgb_model.pkl'
        fingerprint_path = '../../models/stored/xgb_model_fingerprint.txt'

        if not self._is_data_new(model_path, fingerprint_path):
            print("XGBoost: No new data to add! Loading existing model results...")
            xgb_model = self.load_xgboost()
            xgb_predictions = xgb_model.predict(self.X_test)
            xgb_accuracy = accuracy_score(self.y_test, xgb_predictions)
            xgb_classification_report = classification_report(self.y_test, xgb_predictions, zero_division=1)
            xgb_probabilities = xgb_model.predict_proba(self.X_test)[:, 1]

            xgb_checksum = self._calculate_checksum(model_path)
            return xgb_accuracy, xgb_classification_report, xgb_probabilities.tolist(), xgb_checksum

        print("Training XGBoost with new data...")
        xgb_model = XGBClassifier(random_state=42)
        xgb_model.fit(self.X_train, self.y_train)

        xgb_predictions = xgb_model.predict(self.X_test)
        xgb_accuracy = accuracy_score(self.y_test, xgb_predictions)
        xgb_classification_report = classification_report(self.y_test, xgb_predictions, zero_division=1)
        xgb_probabilities = xgb_model.predict_proba(self.X_test)[:, 1]

        # Save model and data fingerprint
        joblib.dump(xgb_model, model_path)
        self._save_data_fingerprint(fingerprint_path)

        xgb_checksum = self._calculate_checksum(model_path)
        return xgb_accuracy, xgb_classification_report, xgb_probabilities.tolist(), xgb_checksum

    def train_lstm(self):
        model_path = '../../models/stored/lstm_model.h5'
        fingerprint_path = '../../models/stored/lstm_model_fingerprint.txt'

        if not self._is_data_new(model_path, fingerprint_path):
            print("LSTM: No new data to add! Loading existing model results...")
            lstm_model = self.load_lstm()
            lstm_predictions = lstm_model.predict(self.X_test)
            lstm_accuracy = accuracy_score(self.y_test, lstm_predictions)
            lstm_classification_report = classification_report(self.y_test, lstm_predictions, zero_division=1)
            lstm_probabilities = lstm_predictions  # Assuming LSTM gives direct probabilities

            lstm_checksum = self._calculate_checksum(model_path)
            return lstm_accuracy, lstm_classification_report, lstm_probabilities.tolist(), lstm_checksum

        print("Training LSTM with new data...")
        # Define and train your LSTM model
        lstm_model = Sequential()
        lstm_model.add(LSTM(100, input_shape=(self.X_train.shape[1], 1), return_sequences=True))
        lstm_model.add(LSTM(100))
        lstm_model.add(Dense(1, activation='sigmoid'))
        lstm_model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

        # Pad the sequences
        X_train_padded = pad_sequences(self.X_train.values)
        X_test_padded = pad_sequences(self.X_test.values)

        lstm_model.fit(X_train_padded, self.y_train, epochs=10, batch_size=64, validation_data=(X_test_padded, self.y_test),
                       callbacks=[EarlyStopping(patience=3)])

        lstm_predictions = lstm_model.predict(X_test_padded)
        lstm_accuracy = accuracy_score(self.y_test, lstm_predictions.round())
        lstm_classification_report = classification_report(self.y_test, lstm_predictions.round(), zero_division=1)
        lstm_probabilities = lstm_predictions

        # Save model and data fingerprint
        lstm_model.save(model_path)
        self._save_data_fingerprint(fingerprint_path)

        lstm_checksum = self._calculate_checksum(model_path)
        return lstm_accuracy, lstm_classification_report, lstm_probabilities.tolist(), lstm_checksum


    @staticmethod
    def load_random_forest():
        return joblib.load('../../models/stored/rf_model.pkl')

    @staticmethod
    def load_xgboost():
        return joblib.load('../../models/stored/xgb_model.pkl')

    @staticmethod
    def load_lstm():
        return load_model('../../models/stored/lstm_model.keras')

    @staticmethod
    def save_results(rf_results, xgb_results, lstm_results):
        results_path = '../../models/evaluate'
        os.makedirs(results_path, exist_ok=True)
        results_file = os.path.join(results_path, 'model_results.txt')

        with open(results_file, "w") as f:
            f.write(f"Random Forest Results:\n")
            f.write(f"Accuracy: {rf_results[0]}\n")
            f.write(f"Classification Report:\n{rf_results[1]}\n")
            f.write(f"Probabilities: {rf_results[2]}\n")
            f.write(f"Checksum: {rf_results[3]}\n\n")

            f.write(f"XGBoost Results:\n")
            f.write(f"Accuracy: {xgb_results[0]}\n")
            f.write(f"Classification Report:\n{xgb_results[1]}\n")
            f.write(f"Probabilities: {xgb_results[2]}\n")
            f.write(f"Checksum: {xgb_results[3]}\n\n")

            f.write(f"LSTM Results:\n")
            f.write(f"Accuracy: {lstm_results[0]}\n")
            f.write(f"Classification Report:\n{lstm_results[1]}\n")
            f.write(f"Probabilities: {lstm_results[2]}\n")
            f.write(f"Checksum: {lstm_results[3]}\n")


if __name__ == "__main__":
    trainer = ModelTrainer(file_path='../../data/dataset/dataset_csv/cuckoo_data_processed.csv')

    rf_results = trainer.train_random_forest()
    xgb_results = trainer.train_xgboost()
    lstm_results = trainer.train_lstm()

    trainer.save_results(rf_results, xgb_results, lstm_results)
    trainer.save_model_checksums(rf_results[3], xgb_results[3], lstm_results[3])