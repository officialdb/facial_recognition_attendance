# Facial Recognition Attendance Management System

A Python-based desktop application that automates student or employee attendance tracking using facial recognition. This was built as a final-year HND Computer Science project at Federal Polytechnic Nekede.

## How the Software Works

The application operates entirely offline and locally on your machine. It consists of four main modules:

1. **User Registration (`registration.py`)**: 
   When a new user is registered, the system opens the webcam and captures 5 distinct frames of their face. It uses the `face_recognition` library to extract a **128-dimensional face encoding** (a mathematical representation of facial features). The average of these 5 encodings is saved into a local database file named `encodings.pkl` alongside the user's Name and Matriculation Number.

2. **Real-time Attendance (`recognition.py`)**: 
   During an attendance session, the webcam continuously monitors for faces. It extracts encodings from detected faces and compares them against the known faces in `encodings.pkl` using Euclidean distance. 
   - If the distance is less than the strict `0.6` threshold, a match is confirmed.
   - The system then checks today's attendance log (e.g., `attendance_2026-03-24.csv`).
   - If the user hasn't been logged today, it appends a new row with their Name, Matric No, Date, and Time. If they are already logged, it simply displays "Already Logged" on the screen to prevent duplicate entries.

3. **Attendance Viewer (`attendance_viewer.py`)**: 
   A user-friendly table interface that reads all `attendance_YYYY-MM-DD.csv` files and displays them in a scrollable list. It also provides an option to export the combined records into a single CSV file.

4. **Main Interface (`main.py`)**: 
   The central Tkinter GUI that ties all the modules together, providing simple buttons to navigate the system without needing to use the command line after setup.


## Prerequisites & Installation

Due to the complex C++ requirements of the `dlib` face recognition engine, running this strictly requires a compatible Python version. **Python 3.11 is highly recommended** because it supports pre-compiled Windows binaries, meaning you do not need to install Visual Studio Build Tools.

### Step 1: Verify Python Version
Ensure you have **Python 3.11** installed on your system. You can download it from [python.org](https://www.python.org/downloads/release/python-3110/).

### Step 2: Open Terminal
Open PowerShell or Command Prompt and navigate to the project folder:
```bash
cd "C:\Project\Facial Recognition\facial_recognition_attendance"
```

### Step 3: Use the Virtual Environment (Recommended)
We have already set up a virtual environment (`venv`) that contains the pre-compiled packages and the correct Numpy version (`<2.0.0`) required to bypass Windows C++ errors.

If you are setting this up on a completely new machine without the `venv` folder, run these commands to recreate the environment and install everything flawlessly:
```bash
# Create a Python 3.11 virtual environment
py -3.11 -m venv venv

# Install the pre-compiled dlib wheel directly
.\venv\Scripts\python.exe -m pip install "https://github.com/z-mahmud22/Dlib_Windows_Python3.x/raw/main/dlib-19.24.1-cp311-cp311-win_amd64.whl"

# Install remaining requirements (OpenCV, numpy, pandas, etc.)
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```


## How to Run the Application

Once your requirements are installed, you *never* run `python main.py` directly (as that might use your system's default Python). You must always launch it through the configured virtual environment.

Run this simple command in your terminal while inside the project folder:
```bash
.\venv\Scripts\python.exe main.py
```

### Using the Application:
1. **Register New User**: Click this first. Enter a name and Matric number, then position your face in front of the webcam. It will capture 5 frames automatically and save your profile.
2. **Start Attendance Session**: Click this to open the live scanner. Walk in front of the camera. A green box will appear with your name and log your attendance. Press `Q` on your keyboard to close the scanner when done.
3. **View Attendance Records**: Click this to see a spreadsheet-like view of everyone who has been marked present. You can export this list to submit to your supervisor.
