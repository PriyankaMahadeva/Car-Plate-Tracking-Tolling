import cv2
import easyocr
import os
import csv
from datetime import datetime
import phonenumbers
from twilio.rest import Client

# Twilio account credentials
account_sid = '***********************************'  
auth_token = '***********************************'
twilio_phone_number = '+12564*****'

# Initialize Twilio client
client = Client(account_sid, auth_token)

# Initialize the plate detector and OCR reader
harcascade = "model/number_plate_by_ajay.xml"
camera_id = 0  # Camera ID, can be changed if you use multiple cameras
cap = cv2.VideoCapture(camera_id)
cap.set(3, 640)  # width
cap.set(4, 480)  # height
# camera_id += 3

min_area = 500  # Minimum area for a plate to be considered valid
accuracy_threshold = 10000  # Area threshold for "accuracy"

# Toll price calculation based on the camera transition
toll_rates = {
    (0, 1): 50,
    (0, 2): 70,
    (0, 3): 90,
    (0, 4): 110,
    (0, 5): 130,
    (1, 2): 40,
    (1, 3): 60,
    (1, 4): 80,
    (1, 5): 100,
    (2, 3): 50,
    (2, 4): 70,
    (2, 5): 90,
    (3, 4): 60,
    (3, 5): 80,
    (4, 5): 50
}

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

# Prepare CSV file to store detected text along with camera information
csv_file = "detected_plates.csv"
if not os.path.exists(csv_file):
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Detected Text", "Camera ID", "Timestamp", "Toll Price"])

# Function to remove duplicate entries when the same text is detected by different cameras
def remove_duplicate_rows(detected_text, camera_id):
    detected_text_clean = "".join(detected_text.split())
    rows = []
    with open(csv_file, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            rows.append(row)

    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        for row in rows:
            row_text_clean = "".join(row[0].split())
            row_camera_id = row[1]
            if detected_text_clean != row_text_clean or row_camera_id == str(camera_id):
                writer.writerow(row)

# Function to check if the detected text exists and handle toll logic
def is_text_in_file(detected_text, camera_id):
    detected_text_clean = "".join(detected_text.split())
    camera_ids = set()
    with open(csv_file, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) > 1:
                row_text_clean = "".join(row[0].split())
                row_camera_id = row[1]
                if detected_text_clean == row_text_clean:
                    camera_ids.add(row_camera_id)
                    if str(camera_id) == row_camera_id:
                        return True, camera_ids
    return False, camera_ids

# Function to find owner phone number from detail.csv
def get_owner_phone(plate_number, detail_file='detail.csv'):
    with open(detail_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Number Plate'].strip().upper() == plate_number.strip().upper():
                return row['Phone']
    return None

# Function to send SMS to the vehicle owner
def send_sms(phone_number, plate_number, toll_rate):
    try:
        parsed_number = phonenumbers.parse(phone_number, "IN")
        formatted_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)

        # Customize your SMS message
        message_body = f"Dear owner of vehicle {plate_number}, a toll of {toll_rate} rupees has been applied for your journey."

        # Send SMS using Twilio
        message = client.messages.create(
            body=message_body,
            from_=twilio_phone_number,
            to=formatted_number
        )

        print(f"SMS sent to {formatted_number} with SID: {message.sid}")
    except phonenumbers.NumberParseException as e:
        print(f"Invalid phone number: {phone_number}. Error: {e}")

# Main loop
while True:
    success, img = cap.read()
    if not success:
        break

    plate_cascade = cv2.CascadeClassifier(harcascade)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    plates = plate_cascade.detectMultiScale(img_gray, 1.1, 4)

    for (x, y, w, h) in plates:
        area = w * h

        if area > min_area:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(img, "Number Plate", (x, y - 5), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 0, 255), 2)

            img_roi = img[y:y + h, x:x + w]
            cv2.imshow("ROI", img_roi)

            if area > accuracy_threshold:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                image_path = f"plates/scanned_img_{timestamp}.jpg"
                cv2.imwrite(image_path, img_roi)
                cv2.rectangle(img, (0, 200), (640, 300), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, "Plate Saved Automatically", (150, 265), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (0, 0, 255), 2)
                cv2.waitKey(500)

                output = reader.readtext(image_path)

                with open(csv_file, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    for box, text, confidence in output:
                        print(f"Detected Text: {text}")
                        print(f"Confidence: {confidence}")

                        text = text.upper()
                        exists, camera_ids = is_text_in_file(text, camera_id)

                        if len(text) > 9 and not exists:
                            text = "".join(text.split())
                            writer.writerow([text, camera_id, timestamp, "N/A"])  # "N/A" for initial toll
                        elif len(text) > 9 and exists:
                            text = "".join(text.split())
                            previous_camera_id = int(next(iter(camera_ids)))
                            toll_rate = toll_rates.get((previous_camera_id, camera_id), 0)
                            if toll_rate > 0:
                                print(f"Toll applied for {text} from camera {previous_camera_id} to camera {camera_id}: {toll_rate} rupees.")
                                # Remove the row for the previous camera
                                remove_duplicate_rows(text, camera_id)
                                writer.writerow([text, camera_id, timestamp, toll_rate])  # Add toll for the exit point

                                # Find the phone number of the vehicle owner
                                owner_phone = get_owner_phone(text)
                                if owner_phone:
                                    # Send SMS to the vehicle owner
                                    send_sms(owner_phone, text, toll_rate)

                os.remove(image_path)

    cv2.imshow("Result", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
