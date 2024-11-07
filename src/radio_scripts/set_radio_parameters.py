import sys
import os

# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import radio_utils

# Default requested values
requested_values = {
    'S0:FORMAT': 26, 
    'S1:SERIAL_SPEED': 57, 
    'S2:AIR_SPEED': 32, 
    'S3:NETID': 18, 
    'S4:TXPOWER': 2, 
    'S5:ECC': 0, 
    'S6:MAVLINK': 1, 
    'S7:OPPRESEND': 1, 
    'S8:MIN_FREQ': 433070, # Default value; can be overridden
    'S9:MAX_FREQ': 433430,  # Default value; can be overridden
    'S10:NUM_CHANNELS': 10, 
    'S11:DUTY_CYCLE': 100, 
    'S12:LBT_RSSI': 0, 
    'S13:MANCHESTER': 0, 
    'S14:RTSCTS': 0, 
    'S15:MAX_WINDOW': 131
}

if __name__ == '__main__':
    # Check if MAX_FREQ is provided as a command-line argument
    if len(sys.argv) > 1:
        try:
            first_port = sys.argv[1]
            second_port = sys.argv[2]
            min_freq = int(sys.argv[3])
            max_freq = int(sys.argv[4])
            requested_values['S8:MIN_FREQ'] = min_freq
            requested_values['S9:MAX_FREQ'] = max_freq

        except ValueError:
            print("Please enter a valid integer for MAX_FREQ.")
            sys.exit(1)
    else:
        first_port = 'COM7'

    # First radio setup
    serial_port = first_port
    baud_rate = 57600
    transmitter = radio_utils.RadioModule(serial_port, baud_rate)
    transmitter.set_params_to_request(requested_values)
    # transmitter.send_at_command('AT&W')
    # print(transmitter.get_current_parameters())

    if len(sys.argv) > 1:
        # Second radio setup
        serial_port = second_port
        baud_rate = 57600
        transmitter = radio_utils.RadioModule(serial_port, baud_rate)
        transmitter.set_params_to_request(requested_values)
        # transmitter.send_at_command('AT&W')
        