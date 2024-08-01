import sys
import os
# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import radio_utils

def main():
    serial_port, baud_rate = radio_utils.pick_pickables()
    transmitter = radio_utils.RadioModule(serial_port,baud_rate)
    try:
        while True:
            command = input("Enter command: ") # in form transmitter.<command>
            try:
                response = eval(command)
                print(response)
            except Exception as e: print(e)
                
    except KeyboardInterrupt:
        print("Stopping.")

if __name__ == "__main__":
    main()