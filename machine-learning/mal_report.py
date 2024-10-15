import json
import os
import torch
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from sklearn.model_selection import train_test_split

# Hàm đọc báo cáo từ file JSON
def read_report(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Hàm trích xuất đặc trưng từ báo cáo
def extract_text_features(report):
    features = []
    # Chuyển đổi thông tin file và chữ ký thành một chuỗi
    for signature in report['statistics']['signatures']:
        if signature['time'] > 0:
            features.append(signature['name'])
    text_data = ' '.join(features)
    return text_data

# Lớp dữ liệu cho Hugging Face
class MalwareDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

# Hàm chính
def main(report_folder_path):
    # Lấy tất cả các file JSON trong thư mục
    report_files = [os.path.join(report_folder_path, file) for file in os.listdir(report_folder_path) if file.endswith('.json')]
    
    # Chuẩn bị dữ liệu
    data = []
    labels = []

    # Lặp qua tất cả các báo cáo mã độc
    for report_file_path in report_files:
        # Đọc báo cáo
        report = read_report(report_file_path)
        
        # Trích xuất đặc trưng từ báo cáo và thêm vào dữ liệu
        data.append(extract_text_features(report))
        labels.append(1)  # Gán nhãn (1 cho mã độc, 0 cho không mã độc), điều chỉnh nhãn nếu cần thiết

    # Chia tập dữ liệu thành training và test sets
    train_texts, test_texts, train_labels, test_labels = train_test_split(data, labels, test_size=0.2)

    # Tải tokenizer và model từ Hugging Face
    tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
    model = AutoModelForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)

    # Tokenize dữ liệu
    train_encodings = tokenizer(train_texts, truncation=True, padding=True, max_length=512)
    test_encodings = tokenizer(test_texts, truncation=True, padding=True, max_length=512)

    # Tạo các dataset cho huấn luyện
    train_dataset = MalwareDataset(train_encodings, train_labels)
    test_dataset = MalwareDataset(test_encodings, test_labels)

    # Thiết lập tham số huấn luyện
    training_args = TrainingArguments(
        output_dir='./results',
        num_train_epochs=3,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=10,
    )

    # Sử dụng Trainer để huấn luyện mô hình
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
    )

    # Huấn luyện mô hình
    trainer.train()

    # Đánh giá mô hình
    results = trainer.evaluate()
    print(f"Evaluation results: {results}")

    # Dự đoán với tất cả báo cáo
    feature_vector = tokenizer(data, truncation=True, padding=True, max_length=512, return_tensors='pt')
    prediction = model(feature_vector['input_ids'], feature_vector['attention_mask'])
    
    # Xử lý dự đoán cho từng báo cáo
    predicted_labels = torch.argmax(prediction.logits, dim=-1).tolist()

    # Kết quả
    for idx, label in enumerate(predicted_labels):
        print(f"Report {report_files[idx]}: {'Malicious file detected!' if label == 1 else 'File is clean.'}")

# Gọi chương trình với đường dẫn tới thư mục chứa báo cáo
if __name__ == "__main__":
    report_folder_path = 'dataset'
    main(report_folder_path)