import sys
import os

# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import radio_utils.radio_utils as radio_utils

requested_values = {
    'S1:SERIAL_SPEED': 38,  # 19, 38, 57, 115, 230[kbaud]
}

if __name__ == '__main__':

    first_port = 'COM4'
    second_port = 'COM5'

    initial_baud_rate = 57600  # 19200 38400, 57600, 115200, 230400
    # radio_utils.pick_pickables()
    # First radio setup
    serial_port = first_port
    transmitter = radio_utils.RadioModule(serial_port, initial_baud_rate)
    transmitter.set_params_to_request(requested_values)
    transmitter.send_at_command('AT&W')
    transmitter.send_at_command('ATZ')

    # print(transmitter.get_current_parameters())

    # Second radio setup
    serial_port = second_port
    transmitter = radio_utils.RadioModule(serial_port, initial_baud_rate)
    transmitter.set_params_to_request(requested_values)
    transmitter.send_at_command('AT&W')
    transmitter.send_at_command('ATZ')

    # sometimes have to reconnect the radios in case of changing baud rate afterwards
        