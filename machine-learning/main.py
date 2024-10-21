from module.report_handle import ReportLoader
from module.string_machine_learning import StringMachineLearning
from module.behavior_machine_learning import BehaviorMachineLearning
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
    dataset_folder = os.path.join(BASE_DIR, "dataset")
    loader = ReportLoader(dataset_folder)

    reports = loader.reports
    labels = loader.labels_list
    strings = loader.strings_list
    behavior_summary = loader.behavior_summary_list

    # Train the model
    ml = StringMachineLearning(labels, strings, debug=True)
    ml.train()
    ml.save_model("string-model.pkl")

    # Train the model
    ml = BehaviorMachineLearning(labels, behavior_summary, debug=True)
    ml.train()
    ml.save_model("behavior-model.pkl")

