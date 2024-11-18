import sqlite3

def monitor_parking_spaces():
    conn = sqlite3.connect('parking_system.db')
    cursor = conn.cursor()

    cursor.execute('SELECT id FROM parking_spaces')
    spaces = cursor.fetchall()

    for space in spaces:
        space_id = space[0]
        # Example: Simulate occupancy change
        is_occupied = random.choice([0, 1])
        cursor.execute('UPDATE parking_spaces SET is_occupied=? WHERE id=?', (is_occupied, space_id))

    conn.commit()
    conn.close()
