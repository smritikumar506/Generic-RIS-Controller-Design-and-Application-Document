import requests
import time
import numpy as np
from collections import Counter

# API endpoints
magnitude_url = 'http://localhost:5000/api/v1/magnitude'  # Magnitude API
ris_config_service_url = 'http://localhost:5001/api/v1/ris_config'  # Endpoint to get RIS config
lut_service_url = 'http://localhost:5002/api/v1/send_config'  # Endpoint for Lookup table creation
rsc_service_url = 'http://localhost:5003/api/v1/configuration_write' # Endpoint for RSC

# Function to get magnitude from an API
def get_magnitude():
    try:
        response = requests.get(magnitude_url)
        if response.status_code == 200:
            data = response.json()
            return data['magnitude']
        else:
            print(f"Error: Received status code {response.status_code} from magnitude API")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

# Function to send the beamforming angle to RSC
def send_to_rsc(beamforming_angle):
    try:
        payload = {'beamforming_angle': beamforming_angle}
        response = requests.post(rsc_service_url, json=payload)
        if response.status_code == 200:
            # print(f"Testing beamforming angle {beamforming_angle}.")
            # print(f"Successfully sent beamforming angle {beamforming_angle} to RSC.")
            # print (f"Best Angle {beamforming_angle}")
            return response.json()  # Return the response from RSC if needed
        else:
            print(f"Error: Received status code {response.status_code} when sending to RSC")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

# Function to query RSC for valid beamforming angles (capability query)
def get_valid_angles():
    try:
        capability_query_url = f'{rsc_service_url}/capability_query'
        response = requests.get(capability_query_url)
        if response.status_code == 200:
            data = response.json()
            return data['valid_angles']
        else:
            print(f"Error: Received status code {response.status_code} during capability query")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    
# Function to find the most frequent beamforming angle from a list
def find_most_frequent_angle(angles):
    if not angles:
        return None
    angle_count = Counter(angles)
    most_frequent_angle = angle_count.most_common(1)[0][0]
    return most_frequent_angle

if __name__ == '__main__':
    best_angles = []  # List to store the 15 best angles
    try:
        print(f"Testing ......")
        while len(best_angles) < 18:  # Collect 15 best angles
            max_magnitude = 0
            # best_beamforming_angle = None
            best_beamforming_angle = 0
            beamforming_angle_range = get_valid_angles()  # Beamforming angles to test

            for beamforming_angle in beamforming_angle_range:
                # Step 1: Query RSC for valid beamforming angles (capability query)
                valid_angles = get_valid_angles()

                if valid_angles is None:
                    print("Could not retrieve valid beamforming angles. Skipping this iteration.")
                    continue

                # Step 2: Check if current beamforming_angle matches any valid angle
                if beamforming_angle in valid_angles:
                    send_to_rsc(beamforming_angle)
                    # time.sleep(2)
                    # Step 4: Get the current magnitude
                    magnitude = get_magnitude()

                    if magnitude is not None:
                        # print(f"Beamforming angle = {beamforming_angle}: Magnitude = {magnitude}")
                        # print(f"Magnitude = {magnitude}")

                        # Update the best beamforming angle if we find a higher magnitude
                        if magnitude > max_magnitude:
                            max_magnitude = magnitude
                            best_beamforming_angle = beamforming_angle
                    else:
                        print(f"Could not retrieve magnitude for angle {beamforming_angle}.")
                else:
                    print(f"Beamforming angle {beamforming_angle} is not valid based on RSC capability query.")

            if best_beamforming_angle is not None:
                # send_to_rsc(best_beamforming_angle)
                best_angles.append(best_beamforming_angle)
                # time.sleep(2)
                # print (f"Best Beamforming Angle {best_beamforming_angle}")

        final_best_angle = find_most_frequent_angle(best_angles)
                
        if final_best_angle is not None:
            print('')
            print('*******************************')
            print('')
            print(f"The Best angle is {final_best_angle}")
            print('')
            print('*******************************')
            print('')
            send_to_rsc(final_best_angle)  # Send the final best angle to RSC
        else:
            print("Could not determine the most frequent beamforming angle.")

            # Sleep for a few seconds before starting the next iteration
            # time.sleep(5)  # Adjust the sleep duration as necessary}
    except KeyboardInterrupt:
        print("Program interrupted. Exiting ....")