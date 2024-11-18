import tkinter as tk
from tkinter import messagebox
import threading
import sqlite3
from authentification import login, create_account  # Import the functions from authentification.py
from monitors import monitor_parking_spaces  # Import the parking space monitoring function


class ParkingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Parking Management System")
        self.logged_in_user = None
        self.create_login_ui()

    def create_login_ui(self):
        self.clear_frame()

        label_username = tk.Label(self.root, text="Username")
        label_username.pack(pady=5)
        self.entry_username = tk.Entry(self.root)
        self.entry_username.pack(pady=5)

        label_password = tk.Label(self.root, text="Password")
        label_password.pack(pady=5)
        self.entry_password = tk.Entry(self.root, show='*')
        self.entry_password.pack(pady=5)

        button_login = tk.Button(self.root, text="Login", command=self.verify_login)
        button_login.pack(pady=10)

        # Add "Create Account" button
        button_create_account = tk.Button(self.root, text="Create Account", command=self.create_account_ui)
        button_create_account.pack(pady=10)

    def verify_login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        user = login(username, password)  # Call the login function from authentification.py

        if user:
            self.logged_in_user = user  # Save the logged-in user
            self.load_main_frame(user)
        else:
            messagebox.showerror("Login Failed", "Incorrect username or password.")

    def load_main_frame(self, user):
        self.clear_frame()

        role = user[3]  # Get the user's role (Manager, Operator, User)

        label_welcome = tk.Label(self.root, text=f"Welcome {user[1]} ({role})")
        label_welcome.pack(pady=10)

        self.start_monitoring_thread()

        # Role-specific actions for Users
        if role == "User":
            button_view_parking = tk.Button(self.root, text="View Available Parking Spaces", command=self.view_parking_spaces)
            button_view_parking.pack(pady=10)

            button_reserve = tk.Button(self.root, text="Reserve a Parking Space", command=self.make_reservation_ui)
            button_reserve.pack(pady=10)

            button_view_reservations = tk.Button(self.root, text="View My Reservations", command=self.view_my_reservations)
            button_view_reservations.pack(pady=10)

            button_cancel_reservation = tk.Button(self.root, text="Cancel Reservation", command=self.cancel_reservation_ui)
            button_cancel_reservation.pack(pady=10)

        button_logout = tk.Button(self.root, text="Logout", command=self.logout)
        button_logout.pack(pady=10)

    def logout(self):
        self.logged_in_user = None
        self.clear_frame()
        self.create_login_ui()

    def view_parking_spaces(self):
        self.clear_frame()

        conn = sqlite3.connect('parking_system.db')
        cursor = conn.cursor()

        # Query to get available parking spaces (not occupied and not reserved)
        cursor.execute('SELECT space_number FROM parking_spaces WHERE is_reserved=0 AND is_occupied=0')
        available_spaces = cursor.fetchall()
        conn.close()

        if available_spaces:
            label_spaces = tk.Label(self.root, text="Available Parking Spaces:")
            label_spaces.pack(pady=5)

            for space in available_spaces:
                label_space = tk.Label(self.root, text=f"Space {space[0]}")
                label_space.pack(pady=5)
        else:
            label_no_spaces = tk.Label(self.root, text="No parking spaces available.")
            label_no_spaces.pack(pady=5)

        button_back = tk.Button(self.root, text="Back", command=lambda: self.load_main_frame(self.logged_in_user))
        button_back.pack(pady=10)

    def make_reservation_ui(self):
        self.clear_frame()

        conn = sqlite3.connect('parking_system.db')
        cursor = conn.cursor()
        cursor.execute('SELECT space_number FROM parking_spaces WHERE is_reserved=0 AND is_occupied=0')
        available_spaces = cursor.fetchall()
        conn.close()

        if available_spaces:
            label_spaces = tk.Label(self.root, text="Select a Parking Space:")
            label_spaces.pack(pady=5)

            self.selected_space = tk.StringVar(self.root)
            dropdown_spaces = tk.OptionMenu(self.root, self.selected_space, *[space[0] for space in available_spaces])
            dropdown_spaces.pack(pady=5)

            label_start_time = tk.Label(self.root, text="Enter Start Time (YYYY-MM-DD HH:MM):")
            label_start_time.pack(pady=5)
            self.entry_start_time = tk.Entry(self.root)
            self.entry_start_time.pack(pady=5)

            label_end_time = tk.Label(self.root, text="Enter End Time (YYYY-MM-DD HH:MM):")
            label_end_time.pack(pady=5)
            self.entry_end_time = tk.Entry(self.root)
            self.entry_end_time.pack(pady=5)

            button_submit = tk.Button(self.root, text="Submit Reservation", command=self.submit_reservation)
            button_submit.pack(pady=10)

        else:
            label_no_spaces = tk.Label(self.root, text="No available parking spaces.")
            label_no_spaces.pack(pady=5)

        button_back = tk.Button(self.root, text="Back", command=lambda: self.load_main_frame(self.logged_in_user))
        button_back.pack(pady=10)

    def submit_reservation(self):
        space_number = self.selected_space.get()
        start_time = self.entry_start_time.get()
        end_time = self.entry_end_time.get()

        conn = sqlite3.connect('parking_system.db')
        cursor = conn.cursor()

        cursor.execute('''
        UPDATE parking_spaces
        SET is_reserved=1
        WHERE space_number=?
        ''', (space_number,))

        cursor.execute('''
        INSERT INTO reservations (user_id, space_id, reservation_type, start_time, end_time)
        VALUES (?, (SELECT id FROM parking_spaces WHERE space_number=?), ?, ?, ?)
        ''', (self.logged_in_user[0], space_number, 'Once', start_time, end_time))

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Parking space reserved successfully!")
        self.load_main_frame(self.logged_in_user)

    def view_my_reservations(self):
        self.clear_frame()

        conn = sqlite3.connect('parking_system.db')
        cursor = conn.cursor()

        cursor.execute('''
        SELECT parking_spaces.space_number, reservations.start_time, reservations.end_time
        FROM reservations
        JOIN parking_spaces ON reservations.space_id = parking_spaces.id
        WHERE reservations.user_id=?
        ''', (self.logged_in_user[0],))

        reservations = cursor.fetchall()
        conn.close()

        if reservations:
            label_reservations = tk.Label(self.root, text="Your Current Reservations:")
            label_reservations.pack(pady=5)

            for reservation in reservations:
                label_reservation = tk.Label(self.root, text=f"Space {reservation[0]} from {reservation[1]} to {reservation[2]}")
                label_reservation.pack(pady=5)
        else:
            label_no_reservations = tk.Label(self.root, text="You have no active reservations.")
            label_no_reservations.pack(pady=5)

        button_back = tk.Button(self.root, text="Back", command=lambda: self.load_main_frame(self.logged_in_user))
        button_back.pack(pady=10)

    def cancel_reservation_ui(self):
        self.clear_frame()

        conn = sqlite3.connect('parking_system.db')
        cursor = conn.cursor()

        cursor.execute('''
        SELECT parking_spaces.space_number
        FROM reservations
        JOIN parking_spaces ON reservations.space_id = parking_spaces.id
        WHERE reservations.user_id=?
        ''', (self.logged_in_user[0],))

        reservations = cursor.fetchall()
        conn.close()

        if reservations:
            label_select_reservation = tk.Label(self.root, text="Select a Reservation to Cancel:")
            label_select_reservation.pack(pady=5)

            self.selected_cancel_space = tk.StringVar(self.root)
            dropdown_reservations = tk.OptionMenu(self.root, self.selected_cancel_space, *[res[0] for res in reservations])
            dropdown_reservations.pack(pady=5)

            button_cancel = tk.Button(self.root, text="Cancel Reservation", command=self.cancel_reservation)
            button_cancel.pack(pady=10)

        else:
            label_no_reservations = tk.Label(self.root, text="You have no active reservations.")
            label_no_reservations.pack(pady=5)

        button_back = tk.Button(self.root, text="Back", command=lambda: self.load_main_frame(self.logged_in_user))
        button_back.pack(pady=10)

    def cancel_reservation(self):
        space_number = self.selected_cancel_space.get()

        conn = sqlite3.connect('parking_system.db')
        cursor = conn.cursor()

        cursor.execute('''
        DELETE FROM reservations
        WHERE space_id = (SELECT id FROM parking_spaces WHERE space_number=?) AND user_id=?
        ''', (space_number, self.logged_in_user[0]))

        cursor.execute('''
        UPDATE parking_spaces
        SET is_reserved=0
        WHERE space_number=?
        ''', (space_number,))

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", f"Reservation for space {space_number} has been canceled.")
        self.load_main_frame(self.logged_in_user)

    def create_account_ui(self):
        self.clear_frame()

        # UI for creating a new account
        label_new_username = tk.Label(self.root, text="New Username")
        label_new_username.pack(pady=5)
        self.entry_new_username = tk.Entry(self.root)
        self.entry_new_username.pack(pady=5)

        label_new_password = tk.Label(self.root, text="New Password")
        label_new_password.pack(pady=5)
        self.entry_new_password = tk.Entry(self.root, show='*')
        self.entry_new_password.pack(pady=5)

        label_role = tk.Label(self.root, text="Role (Manager, Operator, User)")
        label_role.pack(pady=5)
        self.entry_role = tk.Entry(self.root)
        self.entry_role.pack(pady=5)

        button_create = tk.Button(self.root, text="Create Account", command=self.create_account)
        button_create.pack(pady=10)

        button_back = tk.Button(self.root, text="Back", command=self.create_login_ui)
        button_back.pack(pady=10)

    def create_account(self):
        username = self.entry_new_username.get()
        password = self.entry_new_password.get()
        role = self.entry_role.get()

        success, message = create_account(username, password, role)

        if success:
            messagebox.showinfo("Success", message)
            self.create_login_ui()
        else:
            messagebox.showerror("Error", message)

    def start_monitoring_thread(self):
        monitoring_thread = threading.Thread(target=monitor_parking_spaces)
        monitoring_thread.daemon = True
        monitoring_thread.start()

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ParkingApp(root)
    root.mainloop()
