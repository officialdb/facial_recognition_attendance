"""
attendance_viewer.py — Attendance Records Viewer GUI

Provides a Tkinter window with a Treeview table that loads and
displays all dated attendance CSV files, and an export button for
saving the combined records to a new CSV file.
"""

import glob
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Optional

import pandas as pd


class AttendanceViewer(tk.Toplevel):
    """A pop-up window for viewing and exporting attendance records.

    Loads every ``attendance_*.csv`` file found in the current
    directory, displays the rows in a scrollable table, and offers
    an *Export to CSV* button.
    """

    def __init__(self, parent: Optional[tk.Tk] = None) -> None:
        super().__init__(parent)
        self.title("Attendance Records")
        self.geometry("800x500")

        self._build_ui()
        self._load_records()

    # ---- UI construction --------------------------------------------------
    def _build_ui(self) -> None:
        """Build the Treeview table, scrollbar, and export button."""
        # Container frame
        frame = tk.Frame(self, padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # Column definitions
        columns = ("Name", "Matric No.", "Date", "Time", "Status")

        self._tree = ttk.Treeview(
            frame, columns=columns, show="headings", selectmode="browse"
        )

        for col in columns:
            self._tree.heading(col, text=col)
            self._tree.column(col, width=140, anchor=tk.CENTER)

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            frame, orient=tk.VERTICAL, command=self._tree.yview
        )
        self._tree.configure(yscrollcommand=scrollbar.set)

        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Export button
        tk.Button(
            self,
            text="Export to CSV",
            font=("Arial", 12),
            command=self._export,
            width=20,
            height=2,
        ).pack(pady=10)

    # ---- Data loading -----------------------------------------------------
    def _load_records(self) -> None:
        """Read all attendance CSV files and populate the Treeview."""
        csv_files = glob.glob("attendance_*.csv")
        csv_files.sort(reverse=True)  # most recent first

        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                for _, row in df.iterrows():
                    self._tree.insert(
                        "",
                        tk.END,
                        values=(
                            row.get("Name", ""),
                            row.get("Matric No.", ""),
                            row.get("Date", ""),
                            row.get("Time", ""),
                            row.get("Status", ""),
                        ),
                    )
            except Exception:
                # Malformed files are silently skipped
                continue

    # ---- Export ------------------------------------------------------------
    def _export(self) -> None:
        """Save all displayed records to a user-chosen CSV file."""
        path = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Export Attendance Records",
        )

        if not path:
            return

        rows = []
        for item_id in self._tree.get_children():
            rows.append(self._tree.item(item_id, "values"))

        df = pd.DataFrame(
            rows,
            columns=["Name", "Matric No.", "Date", "Time", "Status"],
        )
        df.to_csv(path, index=False)

        messagebox.showinfo(
            "Exported",
            f"Records saved to {path}",
            parent=self,
        )
