import os
from data_processing import load_reports
from training_model import train_model, predict_file
from utils import save_results
from dynamic_analysis import extract_dynamic_features
from static_analysis import prepare_static_data
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # Disable GPU

def pad_static_data(static_data, max_len):
    """Pad or truncate static data to ensure uniform length."""
    padded_data = []
    for data in static_data:
        # If the data is shorter than max_len, pad it with zeros
        if len(data) < max_len:
            data = data + [0] * (max_len - len(data))
        # If the data is longer than max_len, truncate it
        elif len(data) > max_len:
            data = data[:max_len]
        padded_data.append(data)
    return np.array(padded_data, dtype=np.float32)

def main():
    # Directory setup
    reports_dir = 'reports'
    model_dir = 'models'

    # Load and prepare dataset
    print("Loading and preparing dataset...")
    reports = load_reports(reports_dir)
    
    # Extract dynamic and static features from each report
    dynamic_data, static_data, labels = [], [], []
    for report in reports:
        dynamic_data.append(extract_dynamic_features(report))
        static_data.append(prepare_static_data(report)[0])  # Chỉ lấy dữ liệu tĩnh
        labels.append(1 if 'malicious' in report.get('tags', []) else 0)
    
    # Convert dynamic_data and labels to NumPy arrays
    dynamic_data = np.array(dynamic_data)
    labels = np.array(labels)

    print(f"Dynamic data shape: {dynamic_data.shape}")
    print(f"Number of static feature sets: {len(static_data)}")
    print(f"Labels shape: {labels.shape}")

    # Get the maximum length of static_data
    static_shape = max(len(s) for s in static_data)

    # Pad static_data to ensure all elements have the same length
    static_data_padded = pad_static_data(static_data, static_shape)

    # Split data into training and testing sets
    X_train_dyn, X_test_dyn, X_train_static, X_test_static, y_train, y_test = train_test_split(
        dynamic_data, static_data_padded, labels, test_size=0.2, random_state=42
    )

    dynamic_shape = (X_train_dyn.shape[1], 1)  # Định dạng cho LSTM (chuỗi, 1)

    # Train the model
    print("Training model...")
    model = train_model(X_train_dyn, X_train_static, y_train, dynamic_shape, static_shape)

    # Save the trained model
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    model.save(os.path.join(model_dir, "malware_detection_model.keras"))


    # Predict and save results
    results = []
    # Inside your main function
    for idx, report in enumerate(reports):
        result = predict_file(report, model, dynamic_shape, static_shape)
        
        # Construct behavior string
        behavior_str = ', '.join([f"{b['name']} (Severity: {b['severity']})" for b in result['behaviors']])
        
        # Append a dictionary with dynamic, static analysis, and behaviors
        results.append({
            'prediction': result['prediction'],
            'static_analysis': result.get('static_analysis', {}),  # Static analysis results
            'dynamic_analysis': result.get('dynamic_analysis', {}),  # Include dynamic analysis if available
            'behaviors': result['behaviors']  # Behavior results
        })

    # Save results to a file
    save_results(results, "results.txt")

if __name__ == "__main__":
    main()
