import sys
import os
# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import radio_utils

def send_data(serial_conn, data):
    serial_conn.write(data)

def receive_data(serial_conn):
    return serial_conn.read_all()

def main():
    selected_port, detected_baud = radio_utils.pick_pickables()
    try:
        i = 1
        with radio_utils.serial.Serial(selected_port, detected_baud, timeout=1) as ser:

            while True:
                data_to_send = f'{i}'  # Data to send

                send_data(ser, (data_to_send).encode())
                print(f'Sent: {data_to_send}')
                ser.flushOutput()
                print(ser.read_all())
                radio_utils.time.sleep(0.1)  # Send data every second
                # received_data = receive_data(ser)
                # if received_data:
                #      print(f'Received: {received_data}')
                # radio_utils.time.sleep(1)
                i = i + 1
    except radio_utils.serial.SerialException as e:
        print(f'Error: {e}')
    except Exception as e:
        print(f'Unexpected error: {e}')

if __name__ == '__main__':
    main()
    