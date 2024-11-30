# Car-Number-Plates-Detection-Toll-Management

This project implements a toll management system that detects car number plates using OpenCV and EasyOCR. The system calculates toll charges based on vehicle transitions across multiple cameras, records details of detected vehicles, and notifies owners via SMS using Twilio.

## Features

- **Number Plate Detection**: Detects vehicle number plates in real-time using Haar cascades and OCR.
- **Toll Calculation**: Calculates toll charges based on the vehicle's transition between cameras.
- **SMS Notification**: Sends SMS to vehicle owners with toll charges via Twilio.
- **CSV Logging**: Records detected number plates along with timestamps, camera IDs, and toll rates in a CSV file.
- **Duplicate Detection**: Ensures that the same vehicle is not recorded multiple times from different cameras.

## Requirements

- Python 3.x
- OpenCV
- EasyOCR
- Twilio
- phonenumbers
- CSV module

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/ajaythandavamurthy/Car-Number-Plates-Detection-Toll-Management.git
   cd Car-Number-Plates-Detection-Toll-Management

2. Install the required Python libraries:

   ```bash
   pip install opencv-python easyocr twilio phonenumbers

3.  Download the required Haar Cascade model for number plate detection (`model/number_plate_by_ajay.xml`).
    
4.  Set up your Twilio account:
    *   Create an account on [Twilio](https://www.twilio.com/).
    *   Get your `account_sid`, `auth_token`, and Twilio phone number, then update them in the code.

## Configuration

*   **Camera ID**: The system uses the default camera (ID `0`). You can change this if using multiple cameras.
*   **Toll Rates**: Toll prices are defined for transitions between camera pairs. You can modify the `toll_rates` dictionary based on your needs.
*   **Owner Details**: Maintain a `detail.csv` file with columns `Number Plate` and `Phone` to map number plates to vehicle owners and their phone numbers.

## How it Works

1.  The system continuously captures video frames from the camera.
2.  It detects potential number plates using Haar cascade classifiers.
3.  Once a number plate is detected, the system extracts the text using EasyOCR.
4.  If the vehicle is already recorded from another camera, it calculates the toll based on the transition between cameras.
5.  It logs the plate information in a CSV file.
6.  The system sends an SMS notification to the vehicle owner with the toll charge.

## Running the Program

To start the toll management system, simply run the `main.py` script:

```bash
python main.py
