import os
import logging
import pandas as pd
from src.processing.data_extraction import DataExtractor
from src.processing.data_training import DataPreprocessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    dataset_dir = "../../data/dataset" 
    output_dir = "../../data/dataset/dataset_csv" 

    logger.info("Initializing DataExtractor...")
    data_extractor = DataExtractor(dataset_dir=dataset_dir, output_dir=output_dir)

    cuckoo_data = data_extractor.load_cuckoo_dataset()
    if not cuckoo_data:
        logger.error("No data loaded. Exiting.")
        return

    output_filename = "cuckoo_data_extracted"
    data_extractor.extract_cuckoo_data(cuckoo_data, output_filename)

    input_file_path = os.path.join(output_dir, f"{output_filename}.csv")
    logger.info(f"Loading extracted data from {input_file_path}...")
    df = pd.read_csv(input_file_path)

    logger.info("Initializing DataPreprocessor...")
    preprocessor = DataPreprocessor(df)

    processed_data = preprocessor.preprocess()
    logger.info("Data preprocessing completed.")

    logger.info(f"Processed DataFrame shape: {processed_data.shape}")
    logger.info(f"Processed DataFrame columns: {processed_data.columns.tolist()}")

    processed_output_filename = "cuckoo_data_processed"
    processed_output_path = os.path.join(output_dir, f"{processed_output_filename}.csv")
    processed_data.to_csv(processed_output_path, index=False, encoding='utf-8')
    logger.info(f"Processed data saved to: {processed_output_path}")

if __name__ == "__main__":
    main()