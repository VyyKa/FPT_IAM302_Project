from flask import Flask, request, jsonify
import requests
import json
import threading

app = Flask(__name__)

# add a thread function to running the machine learning task
'''
    ml_detaction_status = "" # Malware Detection Status Clean or Malware

    # TODO: Call the Machine Learning model to get the status of the task

    ml_detaction_status = "Clean"

    # Send status after done the Malware Detection task

    api_callback_url = "http://localhost:5000/api/callback"

    response = requests.post(api_callback_url, json={"task_id": task_id, "detection": ml_detaction_status, "status": "success"})
'''


@app.route('/callback', methods=['POST'])
def ml_task_status():
    # Get JSON data from the request body
    data = request.data.decode('utf-8')
    if not data or 'task_id' not in data:
        return jsonify({"error": "task_id is required"}), 200
    
    task_id = json.loads(data).get('task_id')
    
    # Build the report URL to access task status
    report_url = f"localhost:8000/apiv2/tasks/get/report/{task_id}/"
    
    try:
        # Send a GET request to the report endpoint to fetch the status
        response = requests.get(report_url)
        
        # Check if the request was successful
        if response.status_code == 200:
            filename = f"report_{task_id}.json"

            # Save the report to a file
            with open(filename, 'wb') as file:
                file.write(response.content)

            return jsonify({"task_id": task_id}), 200

            # TODO: Call :2 add a thread function to running the machine learning task

        else:
            # TODO: send a request to api_callback_url to update the status of the task to failed

            return jsonify({"error": f"Failed to retrieve report for task_id {task_id}"}), 200

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request to report endpoint failed: {str(e)}"}), 200

if __name__ == '__main__':
    app.run(port=5000)