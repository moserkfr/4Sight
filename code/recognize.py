import face_recognition
import cv2
import numpy as np
import pickle
import urllib.request
from datetime import datetime
import pandas as pd
from flask import Flask, jsonify
from flask_cors import CORS
import os
import threading

# === Flask Setup ===
app = Flask(__name__)
CORS(app)

# === Paths ===
BASE_DIR = os.path.dirname(__file__)
ENCODING_PATH = os.path.join(BASE_DIR, '..', 'data', 'encodings', 'student_encodings.pkl')
ATTENDANCE_FILE = os.path.join(BASE_DIR, '..', 'data', 'attendance.csv')
ESP32_STREAM_URL = "http://0.0.0.0/stream"  # Replace with actual ESP32 IP
CONFIDENCE_THRESHOLD = 0.6

# === Flask Route ===
@app.route('/api/attendance')
def get_attendance():
    # Load master list
    students_df = pd.read_csv(os.path.join(BASE_DIR, '..', 'data', 'students.csv'))
    students_df['name'] = students_df['name'].str.strip().str.lower()

    # Load attendance log
    if os.path.exists(ATTENDANCE_FILE):
        attendance_df = pd.read_csv(ATTENDANCE_FILE)
        attendance_df['name'] = attendance_df['name'].str.strip().str.lower()
        latest_attendance = attendance_df.sort_values(by='timestamp').drop_duplicates('name', keep='last')
    else:
        latest_attendance = pd.DataFrame(columns=['id', 'name', 'timestamp', 'status','confidence   '])

    # Merge and mark absent
    merged = students_df.copy()
    merged['name'] = merged['name'].str.strip().str.lower()
    merged = merged.merge(latest_attendance[['name', 'timestamp', 'status','confidence']], on='name', how='left')
    merged['status'] = merged['status'].fillna('Absent')
    merged['timestamp'] = merged['timestamp'].fillna('')
    merged['confidence'] = merged['confidence'].fillna('')

    # Add new ID
    merged.insert(0, 'id', range(1, len(merged)+1))

    return jsonify(merged.to_dict(orient='records'))


# === Ensure attendance.csv exists ===
os.makedirs(os.path.dirname(ATTENDANCE_FILE), exist_ok=True)
# Ensure attendance file exists with correct headers
if not os.path.exists(ATTENDANCE_FILE) or os.path.getsize(ATTENDANCE_FILE) == 0:
    pd.DataFrame(columns=['id', 'name', 'timestamp', 'status','confidence']).to_csv(ATTENDANCE_FILE, index=False)

# === Attendance Marker ===
recently_marked = {}

def mark_attendance(name, confidence):
    now = datetime.now()
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
    
    if name in recently_marked:
        last_time = recently_marked[name]
        if (now - last_time).seconds < 60:
            return  # Skip duplicate within 1 minute

    df = pd.read_csv(ATTENDANCE_FILE)
    new_id = len(df) + 1
    new_entry = pd.DataFrame([{
        'id': new_id,
        'name': name,
        'timestamp': timestamp,
        'status': 'Present',
        'confidence': round(confidence, 4)
    }])
    new_entry.to_csv(ATTENDANCE_FILE, mode='a', header=False, index=False)
    recently_marked[name] = now
    print(f"[ATTENDANCE] {name} marked present at {timestamp} with confidence {confidence:.4f}")

# === Main Recognition Loop ===
def run_recognition():
    print("[INFO] Loading encodings...")
    with open(ENCODING_PATH, "rb") as f:
        data = pickle.load(f)
    known_encodings = data["encodings"]
    known_names = data["ids"]

    print("[INFO] Connecting to ESP32-CAM stream...")
    stream = urllib.request.urlopen(ESP32_STREAM_URL)
    bytes_data = b''

    while True:
        try:
            bytes_data += stream.read(1024)
            a = bytes_data.find(b'\xff\xd8')
            b = bytes_data.find(b'\xff\xd9')

            if a != -1 and b != -1:
                jpg = bytes_data[a:b+2]
                bytes_data = bytes_data[b+2:]
                frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                face_locations = face_recognition.face_locations(rgb_frame)
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

                
                if face_encodings:    
                    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                        face_distances = face_recognition.face_distance(known_encodings, face_encoding)
                        best_match_index = np.argmin(face_distances)

                        if face_distances[best_match_index] < CONFIDENCE_THRESHOLD:
                            name = known_names[best_match_index]
                            confidence = 1 - face_distances[best_match_index]
                            mark_attendance(name, confidence)

                            # Draw green box and label
                            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                            label = f"{name} ({confidence * 100:.2f}%)"
                            cv2.rectangle(frame, (left, bottom - 20), (right, bottom), (0, 255, 0), cv2.FILLED)
                            cv2.putText(frame, label, (left + 6, bottom - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
                        else:
                            # Unknown face
                            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                            cv2.putText(frame, "Unknown", (left, bottom - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)



                # Optional view
                cv2.imshow("ESP32-CAM", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        except Exception as e:
            print(f"[ERROR] {str(e)}")
            break

    cv2.destroyAllWindows()

# === Start Flask + Recognition ===
if __name__ == '__main__':
    threading.Thread(target=app.run, kwargs={'port': 5000, 'debug': False, 'use_reloader': False}).start()
    run_recognition()
