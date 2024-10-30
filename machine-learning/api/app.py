from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/ml_task_status', methods=['POST'])
def ml_task_status():
    # Get JSON data from the request body
    data = request.get_json()
    if not data or 'task_id' not in data:
        return jsonify({"error": "task_id is required"}), 400
    
    task_id = data['task_id']
    
    # Build the report URL to access task status
    report_url = f"http://localhost:8000/apiv2/tasks/report/{task_id}"
    
    try:
        # Send a GET request to the report endpoint to fetch the status
        response = requests.get(report_url)
        
        # Check if the request was successful
        if response.status_code == 200:
            report_data = response.json()
            status = report_data.get('status', 'Unknown')  # Retrieve the 'status' field from the report
            return jsonify({"task_id": task_id, "status": status}), 200
        else:
            return jsonify({"error": f"Failed to retrieve report for task_id {task_id}"}), response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request to report endpoint failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(port=5000)