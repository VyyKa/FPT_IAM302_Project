import numpy as np
from sklearn.preprocessing import LabelEncoder

file_extension_encoder = LabelEncoder()
is_file_extension_encoder_fitted = False

def extract_static_features(report):
    """Extract static features from the report."""
    file_info = report.get('target', {}).get('file', {})
    
    return {
        'file_size': file_info.get('size', 0),
        'file_extension': file_info.get('type', 'unknown'),
        'md5_hash': file_info.get('md5', ''),
        'sha256_hash': file_info.get('sha256', ''),
        'is_executable': file_info.get('is_executable', False),
        'created_time': file_info.get('created_time', '')
    }

def prepare_static_data(report):
    """Prepare static features for input to the model."""
    static_features = extract_static_features(report)
    file_extension = static_features.get('file_extension', 'unknown')

    global file_extension_encoder
    global is_file_extension_encoder_fitted

    if not is_file_extension_encoder_fitted:
        file_extension_encoder.fit([file_extension])
        is_file_extension_encoder_fitted = True
    elif file_extension not in file_extension_encoder.classes_:
        all_classes = list(file_extension_encoder.classes_) + [file_extension]
        file_extension_encoder.fit(all_classes)

    encoded_file_extension = file_extension_encoder.transform([file_extension])[0]

    static_input = [
        float(static_features.get('file_size', 0)),
        encoded_file_extension,
        1 if static_features.get('is_executable', False) else 0,
        hash_to_numeric(static_features.get('md5_hash', '')),
        hash_to_numeric(static_features.get('sha256_hash', '')),
        timestamp_to_numeric(static_features.get('created_time', ''))
    ]

    return static_input, static_features

def hash_to_numeric(hash_string):
    """Convert hash strings to numeric values."""
    return sum([ord(char) for char in hash_string]) % 100000

def timestamp_to_numeric(timestamp):
    """Convert timestamp to a numeric format."""
    if timestamp == '':
        return 0.0
    try:
        return float(sum(ord(char) for char in timestamp))
    except:
        return 0.0
