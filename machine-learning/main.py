from module.report_handle import ReportLoader, Report
from module.string_machine_learning import StringMachineLearning
from module.behavior_machine_learning import BehaviorMachineLearning
import os
import sys
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
    dataset_folder = os.path.join(BASE_DIR, "dataset")
    loader = ReportLoader(dataset_folder)

    reports = loader.reports
    labels = loader.labels_list
    strings = loader.strings_list
    behavior_summary = loader.behavior_summary_list

    # Train the model
    ml_string = StringMachineLearning(labels, strings, debug=True)
    ml_string.train()
    ml_string.save_model("string-model.pkl")

    # Train the model
    ml_behavior = BehaviorMachineLearning(labels, behavior_summary, debug=True)
    ml_behavior.train()
    ml_behavior.save_model("behavior-model.pkl")

    print("Training completed.")

    args = sys.argv

    if len(args) >= 2:
        # Get the first argument
        file_path_to_predict = args[1]

        # Check if the file exists
        if not os.path.exists(file_path_to_predict):
            print(f"File {file_path_to_predict} does not exist.")
            sys.exit(1)

        # Read the report
        with open(file_path_to_predict, "r") as f:
            report_content = json.load(f)

        # Load the file report
        report = Report(report_content)

        # Predict the string model
        # ml = StringMachineLearning()
        # ml.load_model("string-model.pkl")
        string_prediction = ml_string.predict(report.strings)

        # Predict the behavior model
        # ml = BehaviorMachineLearning()
        # ml.load_model("behavior-model.pkl")
        behavior_prediction = ml_behavior.predict(report.behavior_summary)

        print(f"String prediction: {string_prediction}")
        print(f"Behavior prediction: {behavior_prediction}")
    

