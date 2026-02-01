import face_recognition
import os
import pickle

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
image_dir = os.path.normpath(os.path.join(BASE_DIR, "..", "static", "student_images"))
output_path = os.path.normpath(os.path.join(BASE_DIR, "..", "data", "encodings", "student_encodings.pkl"))

known_encodings = []
known_ids = []

# Loop over each image file
for filename in os.listdir(image_dir):
    if filename.lower().endswith(".jpg"):
        student_id = os.path.splitext(filename)[0]  # e.g., S1 from S1.jpg
        path = os.path.join(image_dir, filename)

        # Load and encode
        image = face_recognition.load_image_file(path)
        face_locations = face_recognition.face_locations(image)

        if face_locations:
            encoding = face_recognition.face_encodings(image, face_locations)[0]
            known_encodings.append(encoding)
            known_ids.append(student_id)
            print(f"[✓] Encoded: {student_id}")
        else:
            print(f"[x] No face found in: {filename}")

# Save encodings
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, "wb") as f:
    pickle.dump({"encodings": known_encodings, "ids": known_ids}, f)

print(f"\n✅ All encodings saved to: {output_path}")
