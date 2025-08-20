from flask import Flask, jsonify, request
import serial
import time

app = Flask(__name__)

# File to store the lookup table
lookup_table_file = 'beamforming_lut.txt'

# Endpoint for querying valid beamforming angles
@app.route('/api/v1/configuration_write/capability_query', methods=['GET'])
def capability_query():
    valid_angles = extract_angles_from_lut()
    if valid_angles:
        return jsonify({'valid_angles': valid_angles}), 200
    else:
        return jsonify({'error': 'No valid beamforming angles found'}), 500

# Function to extract beamforming angles from LUT
def extract_angles_from_lut():
    valid_angles = set()  # To ensure unique angles
    try:
        with open(lookup_table_file, 'r') as file:
            for line in file:
                angle, pattern = line.strip().split(', ')
                valid_angles.add(int(angle))  # Store angles as integers
    except FileNotFoundError:
        print("Lookup table file not found.")
        return None
    except Exception as e:
        print(f"Error reading lookup table: {e}")
        return None
    return list(valid_angles)

# Function to send the beamforming angle to RIS via serial communication
def send_to_ris(beamforming_angle, best_pattern):
    port = '/dev/ttyUSB0'  # Adjust this to the appropriate port
    baud_rate = 115200

    try:
        # Serial communication setup for RIS board
        with serial.Serial(port, baudrate=baud_rate, timeout=1) as ris_serial:
            time.sleep(0.1)  # Allow serial port to initialize
            
            # Clear the input/output buffers before sending data
            ris_serial.reset_input_buffer()
            ris_serial.reset_output_buffer()

            # Send the pattern to RIS
            pattern = f"{best_pattern}"
            ris_serial.write((pattern + '\n').encode('utf-8'))  # Write pattern with newline
            print(f"Sent pattern to RIS: {pattern}")

            # Read response from RIS
            time.sleep(1)  # Give time for RIS to process the command
            if ris_serial.in_waiting > 0:
                response = ris_serial.readline().decode('utf-8').strip()
                print(f"Response from RIS for beamforming angle {beamforming_angle}: {response}")
            else:
                # print("No response from RIS, possible communication issue.")
                print("*************")
                
    except serial.SerialException as e:
        print(f"Serial communication error: {e}")
    except Exception as e:
        print(f"Failed to send pattern to RIS: {e}")

# API endpoint to receive and configure the best beamforming angle from GRC
@app.route('/api/v1/configuration_write', methods=['POST'])
def configure_ris():
    data = request.get_json()
    beamforming_angle = data.get('beamforming_angle')

    # Fetch the best pattern for the provided beamforming angle from the LUT
    best_pattern = fetch_best_pattern_from_lut(beamforming_angle)

    if best_pattern:
        send_to_ris(beamforming_angle, best_pattern)
        return jsonify({'status': 'Success', 'beamforming_angle': beamforming_angle}), 200
    else:
        return jsonify({'error': 'Beamforming angle not found in LUT'}), 404

# Function to fetch the best pattern for a beamforming angle from the LUT
def fetch_best_pattern_from_lut(beamforming_angle):
    try:
        with open(lookup_table_file, 'r') as file:
            for line in file:
                angle, pattern = line.strip().split(', ')
                if int(angle) == beamforming_angle:
                    return pattern
    except FileNotFoundError:
        print("Lookup table file not found.")
        return None
    except Exception as e:
        print(f"Error reading lookup table: {e}")
        return None
    return None

if __name__ == '__main__':
    # Start the Flask server to listen for requests
    app.run(port=5003, debug=False)
