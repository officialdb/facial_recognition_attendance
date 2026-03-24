"""
registration.py — Face Registration Module

Handles user registration by capturing face images via webcam,
computing face encodings, and storing them in a pickle database.
"""

import os
import pickle
import tkinter as tk
from tkinter import messagebox
from typing import Optional

import cv2
import face_recognition
import numpy as np

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
ENCODINGS_FILE = "encodings.pkl"
KNOWN_FACES_DIR = "known_faces"


# ---------------------------------------------------------------------------
# Encoding persistence helpers
# ---------------------------------------------------------------------------
def load_encodings() -> dict:
    """Load the face-encoding database from disk.

    Returns:
        dict: A dictionary with keys ``"names"`` (list of
        ``"Name|Matric"`` strings) and ``"encodings"`` (list of
        128-dimensional NumPy arrays).  Returns an empty structure
        when the file does not yet exist.
    """
    if os.path.exists(ENCODINGS_FILE):
        with open(ENCODINGS_FILE, "rb") as f:
            return pickle.load(f)
    return {"names": [], "encodings": []}


def save_encodings(data: dict) -> None:
    """Serialise the encoding dictionary to *encodings.pkl*.

    Parameters:
        data: Dictionary in the format returned by :func:`load_encodings`.
    """
    with open(ENCODINGS_FILE, "wb") as f:
        pickle.dump(data, f)


# ---------------------------------------------------------------------------
# Face capture & registration
# ---------------------------------------------------------------------------
def register_user(name: str, matric: str) -> bool:
    """Capture 5 face samples from the webcam and register the user.

    The function opens the default webcam, captures frames, detects
    faces, and collects 5 valid face encodings.  The average of those
    encodings is stored in the pickle database alongside the label
    ``"Name|Matric"``.

    Parameters:
        name:   Full name of the user.
        matric: Matriculation number of the user.

    Returns:
        ``True`` if registration succeeded (5 samples captured),
        ``False`` if the user cancelled or the webcam failed.
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return False

    samples: list = []
    count: int = 0

    # Ensure the backup directory exists
    os.makedirs(KNOWN_FACES_DIR, exist_ok=True)

    while count < 5:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert BGR → RGB for face_recognition and ensure it's a contiguous 8-bit array
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb = np.ascontiguousarray(rgb, dtype=np.uint8)
        
        face_locations = face_recognition.face_locations(rgb)

        if face_locations:
            encoding = face_recognition.face_encodings(rgb, face_locations)[0]
            samples.append(encoding)
            count += 1

            # Visual feedback
            cv2.putText(
                frame,
                f"Captured {count}/5",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
            )
        else:
            cv2.putText(
                frame,
                "No face detected - align your face",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2,
            )

        cv2.imshow("Registration - Press Q to cancel", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

    if count < 5:
        return False

    # Compute average encoding from the 5 samples
    avg_encoding = np.mean(samples, axis=0)

    # Persist
    data = load_encodings()

    # Prevent duplicate face registration
    if data["encodings"]:
        distances = face_recognition.face_distance(data["encodings"], avg_encoding)
        if any(d < 0.55 for d in distances):  # slightly stricter threshold for registration
            min_idx = int(np.argmin(distances))
            existing = data["names"][min_idx].split("|")[0]
            messagebox.showerror(
                "Duplicate Face Detected",
                f"This face is already registered to: {existing}",
            )
            return False

    data["names"].append(f"{name}|{matric}")
    data["encodings"].append(avg_encoding)
    save_encodings(data)

    return True


# ---------------------------------------------------------------------------
# Registration GUI
# ---------------------------------------------------------------------------
class RegistrationWindow(tk.Toplevel):
    """A pop-up window for registering a new user.

    Provides text fields for the user's full name and matriculation
    number, plus a button that triggers webcam capture.
    """

    def __init__(self, parent: Optional[tk.Tk] = None) -> None:
        super().__init__(parent)
        self.title("Register New User")
        self.geometry("400x250")
        self.resizable(False, False)

        self._name_var = tk.StringVar()
        self._matric_var = tk.StringVar()

        self._build_ui()

    # ---- UI construction --------------------------------------------------
    def _build_ui(self) -> None:
        """Lay out the registration form widgets."""
        tk.Label(
            self, text="Register New User", font=("Arial", 14, "bold")
        ).pack(pady=10)

        # Full Name
        frame_name = tk.Frame(self)
        frame_name.pack(pady=5)
        tk.Label(frame_name, text="Full Name:", font=("Arial", 11)).pack(
            side=tk.LEFT, padx=5
        )
        tk.Entry(frame_name, textvariable=self._name_var, width=25).pack(
            side=tk.LEFT, padx=5
        )

        # Matric Number
        frame_matric = tk.Frame(self)
        frame_matric.pack(pady=5)
        tk.Label(frame_matric, text="Matric Number:", font=("Arial", 11)).pack(
            side=tk.LEFT, padx=5
        )
        tk.Entry(frame_matric, textvariable=self._matric_var, width=25).pack(
            side=tk.LEFT, padx=5
        )

        # Capture button
        tk.Button(
            self,
            text="Capture Face & Register",
            font=("Arial", 12),
            command=self._submit_registration,
            width=25,
            height=2,
        ).pack(pady=15)

    # ---- Registration handler ---------------------------------------------
    def _submit_registration(self) -> None:
        """Validate inputs and initiate face capture."""
        name = self._name_var.get().strip()
        matric = self._matric_var.get().strip()

        if not name or not matric:
            messagebox.showerror(
                "Error",
                "Please enter both name and matric number.",
                parent=self,
            )
            return

        success = register_user(name, matric)

        if success:
            messagebox.showinfo(
                "Success",
                f"{name} registered successfully!",
                parent=self,
            )
            self.destroy()
        else:
            messagebox.showerror(
                "Error",
                "Registration failed. Please try again.",
                parent=self,
            )
