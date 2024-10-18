from module.report_handle import ReportLoader
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
    dataset_folder = os.path.join(BASE_DIR, "dataset")
    reports = ReportLoader(dataset_folder).reports

    for report in reports:
        print(report.strings)
        print(report.label_string)
        print()
