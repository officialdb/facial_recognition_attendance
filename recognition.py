"""
recognition.py — Real-Time Recognition & Attendance Logging

Runs a live webcam session that detects faces, matches them against
the stored encoding database, and logs attendance to a dated CSV file.
"""

import csv
import os
import pickle
from datetime import datetime
from tkinter import messagebox
from typing import Optional

import cv2
import face_recognition
import numpy as np

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
ENCODINGS_FILE = "encodings.pkl"
ATTENDANCE_FILE = f"attendance_{datetime.now().strftime('%Y-%m-%d')}.csv"


# ---------------------------------------------------------------------------
# Encoding persistence
# ---------------------------------------------------------------------------
def load_encodings() -> dict:
    """Load the face-encoding database from disk.

    Returns:
        dict: A dictionary with keys ``"names"`` and ``"encodings"``.
        Returns an empty structure when the file does not exist.
    """
    if os.path.exists(ENCODINGS_FILE):
        with open(ENCODINGS_FILE, "rb") as f:
            return pickle.load(f)
    return {"names": [], "encodings": []}


# ---------------------------------------------------------------------------
# Attendance logging
# ---------------------------------------------------------------------------
def log_attendance(name: str, matric: str, logged_matrics_session: set) -> bool:
    """Append an attendance record for *name* / *matric* if not already logged.

    The function checks the in-memory set of logged users, and if
    absent, writes a new row to the day's CSV file and updates the set.

    Parameters:
        name:   Full name of the recognised user.
        matric: Matriculation number of the recognised user.
        logged_matrics_session: A memory set of matrics already logged today.

    Returns:
        ``True`` if a new record was written, ``False`` if the user
        was already logged today.
    """
    if matric in logged_matrics_session:
        return False

    # Append new record
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    file_is_new = not os.path.exists(ATTENDANCE_FILE) or os.path.getsize(
        ATTENDANCE_FILE
    ) == 0

    with open(ATTENDANCE_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if file_is_new:
            writer.writerow(["Name", "Matric No.", "Date", "Time", "Status"])
        writer.writerow([name, matric, date_str, time_str, "Present"])

    # Update session cache
    logged_matrics_session.add(matric)
    return True


# ---------------------------------------------------------------------------
# Real-time attendance session
# ---------------------------------------------------------------------------
def run_attendance_session() -> None:
    """Run a live webcam attendance session.

    The function loads the encoding database, opens the default webcam,
    and continuously:

    1. Captures a frame and resizes it to 50 % for faster processing.
    2. Detects face locations and computes encodings on the small frame.
    3. Compares each face against all stored encodings using Euclidean
       distance (threshold **0.6**).
    4. Logs attendance for recognised users (duplicate-safe).
    5. Draws bounding boxes and labels on the **original full-size** frame.
    6. Exits when the user presses **Q**.
    """
    # Guard: no registered users
    if not os.path.exists(ENCODINGS_FILE):
        messagebox.showerror(
            "Error",
            "No registered users found. Please register users first.",
        )
        return

    data = load_encodings()
    if not data["names"]:
        messagebox.showerror(
            "Error",
            "No registered users found. Please register users first.",
        )
        return

    known_encodings = data["encodings"]
    known_names = data["names"]

    # Pre-load today's existing attendance to prevent duplicate logging
    # between separate sessions on the same day
    logged_matrics_session: set = set()
    if os.path.exists(ATTENDANCE_FILE):
        try:
            with open(ATTENDANCE_FILE, "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader, None)  # skip header
                for row in reader:
                    if len(row) >= 2:
                        logged_matrics_session.add(row[1])
        except Exception:
            pass

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Error", "Could not access the webcam.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Resize for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        rgb_small = np.ascontiguousarray(rgb_small, dtype=np.uint8)

        # Detect & encode
        face_locations = face_recognition.face_locations(rgb_small)
        face_encodings = face_recognition.face_encodings(
            rgb_small, face_locations
        )

        for face_encoding, (top, right, bottom, left) in zip(
            face_encodings, face_locations
        ):
            # Compare against known faces
            distances = face_recognition.face_distance(
                known_encodings, face_encoding
            )
            min_idx = int(np.argmin(distances))

            if distances[min_idx] < 0.6:
                label_str = known_names[min_idx]
                name, matric = label_str.split("|", 1)
                logged = log_attendance(name, matric, logged_matrics_session)
                status = "Logged" if logged else "Already Logged"
                display_label = f"{name} ({status})"
                colour = (0, 255, 0)
            else:
                display_label = "Unknown"
                colour = (0, 0, 255)

            # Scale bounding box back to original frame size (×2)
            top *= 2
            right *= 2
            bottom *= 2
            left *= 2

            # Draw rectangle
            cv2.rectangle(frame, (left, top), (right, bottom), colour, 2)

            # Draw label above the box
            cv2.putText(
                frame,
                display_label,
                (left, top - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                colour,
                2,
            )

        # Instruction overlay
        cv2.putText(
            frame,
            "Press Q to end session",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2,
        )

        cv2.imshow("Attendance Session", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
