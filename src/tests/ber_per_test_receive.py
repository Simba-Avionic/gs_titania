import sys
import os
# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import radio_utils
from radio_utils.calculations import average_reports
import radio_utils.testing

# Consts
DEFAULT_PARAMS = radio_utils.testing.DEFAULT_PARAMS

# Force set values (for convenience sake):
DEFAULT_PARAMS['S4:TXPOWER'] = 20
DEFAULT_PARAMS['S2:AIR_SPEED'] = 2
DEFAULT_PARAMS['S10:NUM_CHANNELS'] = 10

def main():
    # serial_port, baud_rate = radio_utils.pick_pickables()
    serial_port = 'COM7'
    baud_rate = 57600
    receiver = radio_utils.RadioModule(serial_port, baud_rate,timeout=0.0001)
    receiver.flushInput()      
    receiver.flushOutput()

    receiver.set_params_to_request(DEFAULT_PARAMS)
    received_frames = []

    try:
        while True:
            byte = receiver.read()
            if not byte == b'':
                received_frames.append(byte)     

    except KeyboardInterrupt:
        print("Stopping receiving.")
    
    print(received_frames)

if __name__ == "__main__":
    main()

