import sys
import os
# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import radio_utils
import time

def send_data(serial_conn, data):
    return serial_conn.write(data)

def receive_data(serial_conn):
    return serial_conn.read()

def main():
    
    if len(sys.argv) > 1:
            selected_port = sys.argv[1]
            detected_baud = 57600
            sending_frequency = int(sys.argv[2]) # how often message is send per second
            print(sending_frequency)
    else:
        # selected_port, detected_baud = radio_utils.pick_pickables()
        selected_port = "COM7"
        detected_baud = 57600
        sending_frequency = 50
    try:
        i = 1
        with radio_utils.serial.Serial(selected_port, detected_baud, timeout=100) as ser:
            ser.flushInput()      
            ser.flushOutput()
            start_time = time.time()                
            while time.time() - start_time < 10:
                time_ms = int(time.time()*1000)
                data_to_send = "G "+str(i)+" "+str(time_ms)
                checksum = i + time_ms
                data_to_send = data_to_send + " " + str(checksum) + " SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSssSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS"
                n = send_data(ser, (data_to_send).encode())
                print(f'Sent {n} bytes: {data_to_send}')
                # radio_utils.time.sleep(1/sending_frequency) 
                i = i + 1
    except radio_utils.serial.SerialException as e:
        print(f'Error: {e}')
    except Exception as e:
        print(f'Unexpected error: {e}')

if __name__ == '__main__':
    main()
    