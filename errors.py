import sqlite3

def log_event(event):
    conn = sqlite3.connect('parking_system.db')
    cursor = conn.cursor()

    cursor.execute("INSERT INTO system_logs (event) VALUES (?)", (event,))
    conn.commit()
    conn.close()

# Example usage:
log_event("System started")
