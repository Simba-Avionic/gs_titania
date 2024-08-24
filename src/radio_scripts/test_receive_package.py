import sys
import os
# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import radio_utils

def send_data(serial_conn, data):
    serial_conn.write(data)

def receive_data(serial_conn):
    return serial_conn.read()

def main():
    selected_port, detected_baud = radio_utils.pick_pickables()
    try:
        with radio_utils.serial.Serial(selected_port, detected_baud, timeout=0.0001) as ser:
            ser.flushInput()      
            ser.flushOutput()              
            while True:
                received_data = receive_data(ser)
                # print(received_data)
                if received_data:
                    print(f'Received: {received_data}')
                    # ser.flushInput()                    
    except radio_utils.serial.SerialException as e:
        print(f'Error: {e}')
    except Exception as e:
        print(f'Unexpected error: {e}')

if __name__ == '__main__':
    main()
    