import sys
import os
# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import radio_utils.radio_utils as radio_utils
from tests.archived.calculations import average_reports
import tests.archived.testing

# Consts
DEFAULT_PARAMS = tests.archived.testing.DEFAULT_PARAMS

# Force set values (for convenience sake):
DEFAULT_PARAMS['S4:TXPOWER'] = 20
DEFAULT_PARAMS['S2:AIR_SPEED'] = 2
DEFAULT_PARAMS['S10:NUM_CHANNELS'] = 10    

def main():
    # serial_port, baud_rate = radio_utils.pick_pickables()
    serial_port = 'COM5'
    baud_rate = 57600
    transmitter = radio_utils.RadioModule(serial_port, baud_rate,timeout=0.0001)
    transmitter.flushInput()      
    transmitter.flushOutput()

    # transmitter.set_params_to_request(DEFAULT_PARAMS)
    
    tests.archived.testing.send_packets_at_defined_speed(transmitter=transmitter,predefined_packets=tests.archived.testing.DEFAULT_PACKET_LIST_16B,number_of_packets_to_send=1024,speed=64)
    

if __name__ == "__main__":
    main()

