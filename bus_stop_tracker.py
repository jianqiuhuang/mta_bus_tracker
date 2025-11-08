"""
uv run --with requests -- python3 bus_stop_tracker.py
"""

import requests
import os
from datetime import datetime
from zoneinfo import ZoneInfo # Built-in to Python 3.9+

# --- Configuration ---
# Get your API key from the environment variables or replace the placeholder
API_KEY = os.getenv('MTA_API_KEY', '966f0407-93de-4c6f-bb59-5814d89e3278')

# The SIRI Stop Monitoring API endpoint (requesting JSON format)
API_URL = "http://bustime.mta.info/api/siri/stop-monitoring.json"

def get_next_bus_arrival_times(stop_id: str, bus_id: str, max_distance_in_miles: int = 5):
    """
    Fetches and prints the "minutes away" for all buses
    approaching a specific stop.
    """
    
    params = {
        'key': API_KEY,
        'MonitoringRef': stop_id,
        'StopMonitoringDetailLevel': 'minimum' # We only need arrival times
    }
    
    # Define the Eastern Timezone
    ET_TIMEZONE = ZoneInfo("America/New_York")
    
    try:
        # Get the current time in Eastern Time
        now = datetime.now(ET_TIMEZONE)

        print(f"=== 🚌 Next {bus_id} Buses for Stop {stop_id} ===")
        print(f"Current Time: {now.strftime('%I:%M:%S %p')}\n")
        
        # Make the GET request to the MTA SIRI API
        response = requests.get(API_URL, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        data = response.json()

        # Navigate to the list of all buses approaching this stop
        stop_visits = data['Siri']['ServiceDelivery']['StopMonitoringDelivery'][0]['MonitoredStopVisit']
        
        if not stop_visits:
            print(f"No buses are currently scheduled to arrive at stop {stop_id}.")
            return

        distinct_buses = set()
        # Iterate through each approaching bus
        for bus in stop_visits:
            journey = bus['MonitoredVehicleJourney']
            arrival = journey['MonitoredCall']
            
            # Extract the key data points
            route_name = journey['LineRef'].split('_')[-1]
            destination = journey['DestinationName']
            distance_text = arrival['Extensions']['Distances']['PresentableDistance']
            distance_in_miles = arrival['Extensions']['Distances']['DistanceFromCall'] * 0.000621371
            
            
            if route_name != bus_id or distance_in_miles >= max_distance_in_miles or (route_name, distance_in_miles) in distinct_buses:
                continue
            
            distinct_buses.add((route_name, distance_in_miles))
            # print(bus)
            print(f"Route: {route_name} (to {destination})")
            print(f"  Status: {distance_text}")
            print(f"  Calculated distance: {distance_in_miles}")

            # Calculate the "minutes away" from the timestamp
            if 'ExpectedArrivalTime' in arrival and arrival['ExpectedArrivalTime']:
                # Parse the ISO 8601 timestamp from the API
                arrival_time = datetime.fromisoformat(arrival['ExpectedArrivalTime'])
                
                # Calculate the time difference in minutes
                time_diff_seconds = (arrival_time - now).total_seconds()
                minutes_away = int(time_diff_seconds / 60)
                
                if minutes_away < 0:
                    print("  Arrival: Arriving now (or just departed)")
                elif minutes_away == 0:
                     print("  Arrival: < 1 minute away")
                else:
                    print(f"  Arrival: {minutes_away} min away (at {arrival_time.strftime('%I:%M %p')})")
            else:
                # Fallback if no real-time data is available (e.g., scheduled time)
                if 'AimedArrivalTime' in arrival and arrival['AimedArrivalTime']:
                    scheduled_time = datetime.fromisoformat(arrival['AimedArrivalTime'])
                    print(f"  Arrival: Scheduled for {scheduled_time.strftime('%I:%M %p')} (no live data)")

            print("-" * 20)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from the MTA API: {e}")
    except (KeyError, IndexError):
        print("Could not parse the API response. This may mean no buses are running.")
    except Exception as e:
        print(f"An error occurred: {e}")
    print("=" * 20)

if __name__ == "__main__":
    if API_KEY == 'YOUR_API_KEY' or not API_KEY:
        print("Please set your MTA_API_KEY in your environment variables")
        print("or replace 'YOUR_API_KEY' in the script with your actual key.")
    else:
        get_next_bus_arrival_times('MTA_805173', 'SIM26')
        get_next_bus_arrival_times('MTA_203532', 'SIM25')
        get_next_bus_arrival_times('MTA_201106', 'SIM1C')