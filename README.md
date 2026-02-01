# 4Sight - Smart Attendance System

4Sight is a real-time, face recognition-based attendance automation system. It uses an **ESP32-CAM** to stream video footage to a central server, where a **Python** backend processes faces using computer vision. Attendance records are logged instantly and displayed on a modern **React** dashboard.

## 🚀 Features
* **Real-time Face Recognition**: accurate identification using `dlib` and `face_recognition`.
* **Wireless Streaming**: ESP32-CAM streams video over WiFi to the processing server.
* **Duplicate Prevention**: Smart logic prevents marking the same student multiple times within 60 seconds.
* **Live Dashboard**: A React + TypeScript web interface to view attendance logs and confidence scores.
* **CSV Logging**: Automatically maintains an Excel-compatible `attendance.csv` file.

## 🛠️ Tech Stack
* **Hardware**: ESP32-CAM (AI-Thinker Model)
* **Backend**: Python, Flask, OpenCV, Face Recognition lib, Pandas
* **Frontend**: React (Vite), TypeScript, CSS
* **Data**: Pickle (Encodings), CSV (Logs)

## 📂 Project Structure
```text
4Sight/
├── code/
│   ├── recognize.py          # Main backend server & recognition loop
│   ├── enroll_faces.py       # Script to train/encode new student faces
│   └── convert.py            # Utility script
├── data/
│   ├── encodings/            # Stores generated face encodings (.pkl)
│   ├── students.csv          # Master list of student details
│   └── attendance.csv        # Generated attendance log
├── esp32/
│   └── esp32_stream/         # Arduino sketch for the camera
├── react-app/                # Frontend Dashboard source code
├── static/
│   └── student_images/       # Source images for training
└── requirements.txt          # Python dependencies
