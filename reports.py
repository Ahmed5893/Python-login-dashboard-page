import sqlite3

def generate_occupancy_report():
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
