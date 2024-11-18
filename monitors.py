import sqlite3
import requests
import time

# Function to get parking space status from a real sensor API
def get_parking_space_status_from_api():
    # Replace this URL with your real sensor API endpoint
    api_url = "https://api.example.com/parking-spaces"  # <-- Real API URL goes here

    try:
        response = requests.get(api_url)

        # Check if the request was successful (HTTP status 200)
        if response.status_code == 200:
            return response.json()  # Assuming the API returns JSON data
        else:
            print(f"Error: Failed to fetch data from API. Status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error: Could not connect to the API. {e}")
        return None

# Update parking spaces in the database with data from the sensor API
def update_parking_spaces_with_sensor_data():
    sensor_data = get_parking_space_status_from_api()

    if sensor_data:
        conn = sqlite3.connect('parking_system.db')
        cursor = conn.cursor()

        # Iterate over the parking space data from the API and update the database
        for space in sensor_data:
            space_id = space['id']  # The ID of the parking space from the API
            is_occupied = space['is_occupied']  # Boolean: 1 if occupied, 0 if free
            is_reserved = space.get('is_reserved', 0)  # Optional: Set to 0 if not provided by API

            # Update the parking space in the database with the new status
            cursor.execute('''
                UPDATE parking_spaces
                SET is_occupied=?, is_reserved=?
                WHERE id=?
            ''', (is_occupied, is_reserved, space_id))

        conn.commit()
        conn.close()

        print("Parking spaces updated with real-time data from sensor API.")
    else:
        print("No data received from the API.")

# Run the update process periodically (e.g., every 5 minutes)
def monitor_parking_spaces(interval=300):
    while True:
        update_parking_spaces_with_sensor_data()  # Fetch and update parking spaces
        time.sleep(interval)  # Wait for the specified interval (in seconds)

if __name__ == "__main__":
    # Start monitoring parking spaces (updates every 5 minutes by default)
    monitor_parking_spaces(interval=300)
