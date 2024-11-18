import sqlite3

def login(username, password):
    conn = sqlite3.connect('parking_system.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    
    conn.close()
    
    if user:
        return user
    else:
        return None

# Function to create a new account
def create_account(username, password, role):
    conn = sqlite3.connect('parking_system.db')
    cursor = conn.cursor()

    # Check if the username already exists
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    existing_user = cursor.fetchone()

    if existing_user:
        return False, "Username already exists."

    # Insert new user into the database
    cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
    conn.commit()
    conn.close()

    return True, "Account created successfully."