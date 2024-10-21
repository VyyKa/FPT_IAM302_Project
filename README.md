# Hybrid Malware Analysis System

![Banner](assets/banner.jpg)

Welcome to the Hybrid Malware Analysis System project repository. This system integrates machine learning with CAPEv2 sandbox to provide detailed hybrid analysis of potentially malicious files. Developed by the Cybersec_N00bers team as part of the IAM302 course at FPT University, this project aims to streamline the malware analysis process through automation and enhanced detection capabilities.


## Objective

The primary objective of this project is to develop a robust, automated malware analysis system that combines dynamic behavioral analysis with machine learning. By doing so, the system aims to improve the accuracy and efficiency of malware detection and analysis, making it easier for cybersecurity professionals and researchers to identify threats in a timely and effective manner. This system is designed to be user-friendly, scalable, and adaptable to various malware analysis needs.

## Features

- **Hybrid Analysis**: Utilizes CAPEv2 sandbox for dynamic behavioral analysis of malware.
- **Automation**: System setup is automated with an All-In-One script, simplifying installation and configuration.
- **Containerized**: Runs entirely within Docker containers, ensuring consistency across different environments and simplifying system dependencies.
- **Cross-platform Analysis**: Capable of analyzing malware targeted at various operating systems, enhancing the versatility of malware research.
- **Machine Learning Integration**: Employs machine learning algorithms to distinguish between clean and malicious files effectively.

## System Requirements

- **Operating System**: Tested on Ubuntu Desktop LTS versions 22.04 and 23.04.
- **Virtualization**: VirtualBox is required for hosting the sandbox environment.
- **Root Privileges**: Script execution requires root access to manage system services and dependencies.

## Setup

1. **Clone the Repository**:
   ```
   git clone https://github.com/CyberSecN00bers/FPT_IAM302_Project.git
   cd FPT_IAM302_Project
   ```

2. **Run All-In-One Setup Script**:
   ```bash
   sudo ./AIO.sh
   ```
   This script will set up the environment, including Docker, VirtualBox, and all necessary dependencies.

## Usage

After installation, the system is ready to analyze files. Place the suspicious file in the designated directory and the system will automatically process and generate a report within the Docker container.

## Contributing

Contributions to this project are welcome. Please fork the repository, make your changes, and submit a pull request for review.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Acknowledgments

- Special thanks to FPT University and the IAM302 course instructors for guidance and support.
- This project was inspired by the need for accessible, efficient malware analysis tools in the cybersecurity community.

---
