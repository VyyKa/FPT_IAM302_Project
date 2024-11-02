import os
import json
import numpy as np
from static_analysis import extract_static_features
from dynamic_analysis import extract_dynamic_features

def load_reports(directory):
    """Load JSON reports from the specified directory."""
    reports = []
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            with open(os.path.join(directory, filename), 'r') as f:
                reports.append(json.load(f))
    return reports

def prepare_dataset(reports):
    """Prepare dynamic and static datasets from reports."""
    dynamic_data = []
    static_data = []
    labels = []

    for report in reports:
        dynamic_features = extract_dynamic_features(report)  # Implement this function based on report structure
        static_features = prepare_static_data(report)  # Implement this function based on report structure

        dynamic_data.append(dynamic_features)
        static_data.append(static_features)
        labels.append(report.get('tags', []))

    return np.array(dynamic_data), static_data, labels  # Ensure static_data is flexible

def prepare_static_data(report):
    """Prepare static features for input to the model."""
    # Similar to previous static data processing but flexible
    static_features = extract_static_features(report)  # Implement this function based on report structure

    static_input = {
        'file_size': float(static_features.get('file_size', 0)),
        'file_extension': static_features.get('file_extension', 'unknown'),
        'is_executable': 1 if static_features.get('is_executable', False) else 0,
        # Add more fields as needed, ensure they are properly handled
    }
    return static_input  # Return as dict for flexibility
