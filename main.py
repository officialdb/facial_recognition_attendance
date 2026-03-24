"""
main.py — Application Entry Point & Main GUI Window

Launches the Facial Recognition Attendance System main menu with
buttons for registration, attendance sessions, record viewing, and exit.
"""

import tkinter as tk

from attendance_viewer import AttendanceViewer
from recognition import run_attendance_session
from registration import RegistrationWindow


class AttendanceApp(tk.Tk):
    """Main application window for the Facial Recognition Attendance System.

    Inherits from :class:`tk.Tk` and provides four action buttons:
    register a new user, start an attendance session, view records,
    and exit.
    """

    def __init__(self) -> None:
        super().__init__()
        self.title("Facial Recognition Attendance System")
        self.geometry("600x400")
        self.configure(bg="#f0f0f0")
        self.resizable(False, False)

        self._build_ui()

    # ---- UI construction --------------------------------------------------
    def _build_ui(self) -> None:
        """Create the header label and four action buttons."""
        # Header
        tk.Label(
            self,
            text="Facial Recognition Attendance System",
            font=("Arial", 16, "bold"),
            bg="#f0f0f0",
        ).pack(pady=20)

        # Button definitions: (label, callback)
        buttons = [
            ("Register New User", self._open_registration),
            ("Start Attendance Session", self._start_session),
            ("View Attendance Records", self._open_viewer),
            ("Exit", self.destroy),
        ]

        for text, command in buttons:
            tk.Button(
                self,
                text=text,
                font=("Arial", 12),
                width=30,
                height=2,
                command=command,
            ).pack(pady=8)

    # ---- Button handlers --------------------------------------------------
    def _open_registration(self) -> None:
        """Open the registration window as a child Toplevel."""
        RegistrationWindow(self)

    def _start_session(self) -> None:
        """Run a blocking attendance session via OpenCV."""
        run_attendance_session()

    def _open_viewer(self) -> None:
        """Open the attendance records viewer as a child Toplevel."""
        AttendanceViewer(self)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app = AttendanceApp()
    app.mainloop()
