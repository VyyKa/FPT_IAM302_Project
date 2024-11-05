import os
import shutil
import sys
import json
import logging
from src.processing.data_extraction import DataExtractor
from src.processing.data_training import DataPreprocessor
from src.training.trainer import ModelTrainer
from src.evaluation.evaluator import ReportAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_DIR = "models/stored"
REPORT_DIR = "data/reports"
RESULTS_DIR = "data/results"
CUCKOO_DIR = "data/dataset/cuckoo"
DATASET_CSV_DIR = "dataset_csv"

def save_user_file(file_path):
    filename = os.path.basename(file_path)
    dest_path = os.path.join(REPORT_DIR, filename)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        with open(dest_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=4)
        print(f"File saved to {dest_path}")
    except Exception as e:
        print(f"Error saving file: {e}")
        sys.exit(1)
    return dest_path

# Error
def update_model(report_path):
    extractor = DataExtractor(report_path, DATASET_CSV_DIR)

    cuckoo_data = extractor.load_cuckoo_dataset(report_path)

    base_name = os.path.splitext(os.path.basename(report_path))[0]
    output_filename = os.path.join(DATASET_CSV_DIR, f"{base_name}_processed.csv")

    extracted_data = extractor.extract_cuckoo_data(cuckoo_data, output_filename)
    preprocessor = DataPreprocessor(extracted_data)
    preprocessed_data = preprocessor.preprocess()

    preprocessed_data.to_csv(output_filename, index=False, encoding='utf-8')
    logger.info(f"Data from your report has been saved at {output_filename}")

    training = ModelTrainer(output_filename)

    training.train_random_forest()
    training.train_xgboost()
    training.train_lstm()

    logger.info("Model updated with new data.")

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <filename.json>")
        sys.exit(1)

    user_file = sys.argv[1]
    input_file = save_user_file(user_file)

    analyzer = ReportAnalyzer(
        rf_model_path='models/stored/rf_model.pkl',
        xgb_model_path='models/stored/xgb_model.pkl',
        lstm_model_path='models/stored/lstm_model.keras',
        reports_dir=f'{input_file}',
        results_dir='data/results'
    )
    analyzer.analyze_reports()

    shutil.copy(input_file, CUCKOO_DIR)
    logger.info(f"Copied file from {input_file} to {CUCKOO_DIR}")
    # update_model(input_file)

if __name__ == "__main__":
    main()
