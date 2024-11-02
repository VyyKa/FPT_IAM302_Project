import numpy as np

def extract_dynamic_features(report):
    """Extract dynamic features such as processing times, handling variable lengths."""
    processing_times = report.get('statistics', {}).get('processing', [])
    
    # Create a list of processing times
    times = [process.get('time', 0) for process in processing_times]

    # Pad or truncate times to ensure they fit the model input size (e.g., pad to length 12)
    max_len = 12
    if len(times) < max_len:
        times += [0] * (max_len - len(times))  # Pad with zeros if too short
    return np.array(times[:max_len], dtype=np.float32)

def analyze_behaviors(report):
    """Analyze behaviors from the report, ensuring flexibility with variable-sized data."""
    signatures = report.get('statistics', {}).get('signatures', [])
    
    # Collect behaviors and map them to user-friendly descriptions
    behaviors = []
    for sig in signatures:
        behavior_name = sig['name']
        description = sig.get('description', 'No description available')
        severity = sig.get('severity', 'Unknown')

        # Add a readable entry for each behavior detected
        behaviors.append({
            'name': behavior_name,
            'description': description,
            'severity': severity
        })

    # Handle cases where there are no behaviors detected
    if not behaviors:
        behaviors.append({'name': 'No suspicious behaviors detected', 'description': '', 'severity': ''})

    return behaviors
