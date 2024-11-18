import tkinter as tk
from tkinter import messagebox
import sqlite3

# User login function
def login(username, password):
    conn = sqlite3.connect('parking_system.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

# Main Parking App Class
class ParkingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Parking Management System")
        self.create_login_ui()

    def create_login_ui(self):
        self.clear_frame()

        label_username = tk.Label(self.root, text="Username")
        label_username.pack()
        self.entry_username = tk.Entry(self.root)
        self.entry_username.pack()

        label_password = tk.Label(self.root, text="Password")
        label_password.pack()
        self.entry_password = tk.Entry(self.root, show='*')
        self.entry_password.pack()

        button_login = tk.Button(self.root, text="Login", command=self.verify_login)
        button_login.pack()

    def verify_login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        user = login(username, password)

        if user:
            self.load_main_frame(user)
        else:
            messagebox.showerror("Login Failed", "Incorrect username or password.")

    def load_main_frame(self, user):
        self.clear_frame()
        role = user[3]

        label = tk.Label(self.root, text=f"Welcome {user[1]} ({role})")
        label.pack()

        if role == "Manager":
            button_report = tk.Button(self.root, text="Generate Report", command=self.generate_report)
            button_report.pack()

    def generate_report(self):
        self.clear_frame()
        report_text = self.generate_occupancy_report()
        label_report = tk.Label(self.root, text=report_text)
        label_report.pack()

    def generate_occupancy_report(self):
        conn = sqlite3.connect('parking_system.db')
        cursor = conn.cursor()
        cursor.execute('''
        SELECT zone_id, COUNT(*) AS total_spaces, SUM(is_occupied) AS occupied_spaces
        FROM parking_spaces
        GROUP BY zone_id
        ''')
        report = cursor.fetchall()
        conn.close()

        report_text = "Zone Occupancy Report:\n"
        for row in report:
            zone_id, total_spaces, occupied_spaces = row
            report_text += f"Zone {zone_id}: {occupied_spaces}/{total_spaces} spaces occupied\n"
        return report_text

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

# Initialize the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = ParkingApp(root)
    root.mainloop()
