"""
uv run --with requests -- python3 bus_route_tracker.py
"""

import requests
import os

# --- Configuration ---
# Get your API key from the environment variables or replace the placeholder
API_KEY = os.getenv('MTA_API_KEY', '966f0407-93de-4c6f-bb59-5814d89e3278')

# The route you want to track (e.g., B46). 
# Note: You must use the full ID format, which you can get from the OneBusAway API.
ROUTE_ID = 'MTA NYCT_SIM26' 

# The SIRI Vehicle Monitoring API endpoint (requesting JSON format)
API_URL = "http://bustime.mta.info/api/siri/vehicle-monitoring.json"

def get_bus_locations_siri():
    """
    Fetches and prints the real-time locations of buses for a specific
    MTA route using the SIRI VehicleMonitoring API.
    """
    
    params = {
        'key': API_KEY,
        'LineRef': ROUTE_ID,
        'VehicleMonitoringDetailLevel': 'calls'  # 'calls' gives more detail
    }

    try:
        # Make the GET request to the MTA SIRI API
        response = requests.get(API_URL, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        data = response.json()
        
        # Navigate the complex SIRI JSON structure
        vehicle_activity = data['Siri']['ServiceDelivery']['VehicleMonitoringDelivery'][0]['VehicleActivity']
        
        print(f"Tracking buses for route: {ROUTE_ID} 🚌\n")
        
        if not vehicle_activity:
            print("No active buses found for this route at the moment.")
            return

        # Iterate through each active bus
        for bus in vehicle_activity:
            journey = bus['MonitoredVehicleJourney']
            position = journey['VehicleLocation']
            
            # The VehicleRef is usually formatted like 'MTA NYCT_4567'
            bus_id = journey['VehicleRef'].split('_')[-1]
            
            print(f"Bus ID: {bus_id}")
            print(f"  Latitude: {position['Latitude']}")
            print(f"  Longitude: {position['Longitude']}")
            
            # Get next stop info, if available
            if journey.get('OnwardCalls'):
                next_stop = journey['OnwardCalls']['OnwardCall'][0]
                stop_name = next_stop['StopPointName']
                distance = next_stop['Extensions']['Distances']['PresentableDistance']
                print(f"  Next Stop: {stop_name} ({distance})")
            
            print("-" * 20)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from the MTA API: {e}")
    except (KeyError, IndexError):
        # This can happen if the API response structure is not as expected
        # (e.g., no 'VehicleActivity' field if no buses are running)
        print(f"Could not parse the API response for {ROUTE_ID}.")
        print("This often means there are no active buses on this route right now.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if API_KEY == 'YOUR_API_KEY' or not API_KEY:
        print("Please set your MTA_API_KEY in your environment variables")
        print("or replace 'YOUR_API_KEY' in the script with your actual key.")
    else:
        get_bus_locations_siri()