import sys
import os

# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import radio_utils.radio_utils as radio_utils
import time



def send_data(serial_conn, data):
    """Sends data through the serial connection."""
    return serial_conn.write(data)

def main():
    # Retrieve command-line arguments or set defaults
    if len(sys.argv) > 1:
        selected_port = sys.argv[1]
        sending_frequency = int(sys.argv[2])  # Messages sent per second
    else:
        selected_port, sending_frequency = radio_utils.pick_pickables()
        # selected_port = "COM7"
        # sending_frequency = 50

    detected_baud = 115200
    
    try:
        i = 1
        with radio_utils.serial.Serial(selected_port, detected_baud, timeout=0.000001) as ser:
            ser.flushInput()
            ser.flushOutput()
            
            while True:
                # Generate message content
                time_ms = int(time.time() * 1000)  # Timestamp in milliseconds
                data_to_send = f"G {i} {time_ms} {i + time_ms} "

                # Pad the message to reach exactly 50 bytes
                padded_data = data_to_send.ljust(49, '0') + "S"  # Ensures "S" is the last character

                # Send the padded message
                n = send_data(ser, padded_data.encode())
                print(f'Sent {n} bytes: {padded_data.encode()}')

                # Wait for the next transmission
                time.sleep(1 / sending_frequency)
                i += 1

    except radio_utils.serial.SerialException as e:
        print(f'Error: {e}')
    except Exception as e:
        print(f'Unexpected error: {e}')

if __name__ == '__main__':
    main()