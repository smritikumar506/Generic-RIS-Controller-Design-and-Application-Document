#LUT is populated with the transmitter at 90 degrees against the board.
#Steps:
# - get beamforming_angle
# - generate random patterns
# - find the one that maximizes the magnitude
# - populate LUT using the maximizing pattern
# Experimental Setup: CE <--> LUT_Calibration <--> RIS
# run the codes CE.py and LUT_Calibration.py

from flask import Flask, jsonify, request
import os
import serial
import time
import random
import requests

# Serial communication setup for RIS board
port = '/dev/ttyUSB0'  # Adjust this to the appropriate port
baud_rate = 115200

magnitude_url = 'http://localhost:5000/api/v1/magnitude'  # Magnitude API

# Function to get magnitude from an API
def get_magnitude():
    try:
        response = requests.get(magnitude_url)
        if response.status_code == 200:
            data = response.json()
            return data['magnitude']
        else:
            print(f"Error: Received status code {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

# File to store the lookup table
lookup_table_file = 'beamforming_lut.txt'

def send_to_lut(beamforming_angle, best_pattern):
    """
    Save the LUT
    """
    with open(lookup_table_file, 'a') as file:
        file.write(f"{beamforming_angle}, {best_pattern}\n")
    print(f"Saved beamforming angle: {beamforming_angle}, pattern: {best_pattern} to the lookup table.")
   
    
if __name__ == '__main__':
    port = '/dev/ttyUSB0'  # Adjust this to the appropriate port
    baud_rate = 115200

    # Create a new serial object for RIS communication
    ris_serial = serial.Serial(port, baudrate=baud_rate, timeout=1)

    # Clear input buffer
    time.sleep(0.1)  # Wait for a moment
    while ris_serial.in_waiting > 0:
        ris_serial.readline()  # Clear out any residual data
        time.sleep(3)  # Pause briefly
    print("RIS Board is now connected")
    
    beamforming_angle=input('Please provide the beamforming_angle value for the Rx ...')
    best_pattern=""

    set_vocublary = ["FFFF","0000"]
    max_mag=0
    
    for _ in range(100):

        #generate a random pattern and send to RIS
        res = ''.join(random.choices(set_vocublary,k=16)) # initializing size of string
        pattern = '!0X'+str(res)
        ris_serial.write((pattern + '\n').encode('utf-8'))  # Write pattern with newline
        response = ris_serial.readline().decode('utf-8').strip()  # Read response
        print(f"Response from setting a pattern: {response}")
        time.sleep(1)

        # Get the current magnitude under this random pattern
        magnitude = get_magnitude()
        if magnitude is not None and magnitude > max_mag:
            max_mag=magnitude
            print(f"Current magnitude: {magnitude}")
            best_pattern = pattern
            print(f"Received RIS configuration: Best Pattern: {best_pattern}")
            
        # Sleep for 1 second before making the next request
        time.sleep(2)
    # Save the direction and best pattern in the Lookup Table
    send_to_lut(beamforming_angle, best_pattern)
    