import os
from .utils import read_report


class Report:
    def __init__(self, report_raw_data: dict, label: int = None):
        self.report_raw_data = report_raw_data
        self.__label = label
        self.__parse()

    def __parse(self):
        """
        Parse the raw data to extract the necessary information
        """
        self.__strings = (
            self.report_raw_data.get("target", {}).get("file", []).get("strings", [])
        )

    @property
    def strings(self) -> list:
        """
        Return the strings
        """
        return self.__strings

    @property
    def label(self) -> int:
        """
        Return the label
        """
        return self.__label

    @property
    def label_string(self) -> str:
        """
        Return the label in string format
        """
        return "malicious" if self.__label == 1 else "clean"


class ReportLoader:
    def __init__(self, dataset_folder: str):
        """
        Initialize the loader with the dataset folder
        """
        self.dataset_folder = dataset_folder
        clean_path = os.path.join(self.dataset_folder, "clean")
        malicious_path = os.path.join(self.dataset_folder, "malicious")

        # Get all the files in the clean and malicious folders
        clean_files = [
            os.path.join(clean_path, file)
            for file in os.listdir(clean_path)
            if file.endswith(".json")
        ]
        malicious_files = [
            os.path.join(malicious_path, file)
            for file in os.listdir(malicious_path)
            if file.endswith(".json")
        ]

        # Prepare the data
        raw_data = []
        labels = []

        # Loop through all the clean reports
        for report_file_path in clean_files:
            report = read_report(report_file_path)

            # Check if the report is None
            if report is None:
                continue
            raw_data.append(report)
            labels.append(0)  # 0 is clean

        # Loop through all the malicious reports
        for report_file_path in malicious_files:
            report = read_report(report_file_path)

            # Check if the report is None
            if report is None:
                continue
            raw_data.append(report)
            labels.append(1)  # 1 is malicious

        self.__reports = [
            Report(report, label) for report, label in zip(raw_data, labels)
        ]

    @property
    def reports(self) -> list:
        return self.__reports

    @property
    def clean_reports(self) -> list:
        return [report for report in self.__reports if report.label == 0]
    
    @property
    def malicious_reports(self) -> list:
        return [report for report in self.__reports if report.label == 1]
    
    @property
    def labels_list(self) -> list:
        return [report.label for report in self.__reports]
    
    @property
    def strings_list(self) -> list:
        return [report.strings for report in self.__reports]