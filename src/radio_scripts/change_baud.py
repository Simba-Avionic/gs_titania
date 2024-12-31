import sys, os
# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import radio_utils.radio_utils as radio_utils

def change_baud(first_port,second_port,initial_baud_rate,new_baud_rate):

    requested_values = {'S1:SERIAL_SPEED': new_baud_rate}  # 19, 38, 57, 115, 230 [kbaud]
    
    # First radio setup
    radio = radio_utils.RadioModule(first_port, initial_baud_rate)
    radio.set_params_to_request(requested_values)
    radio.send_at_command('AT&W')
    radio.send_at_command('ATZ')
    radio.close()

    # print(transmitter.get_current_parameters())

    # Second radio setup
    radio = radio_utils.RadioModule(second_port, initial_baud_rate)
    radio.set_params_to_request(requested_values)
    radio.send_at_command('AT&W')
    radio.send_at_command('ATZ')

if __name__ == '__main__':

    # radio_utils.pick_pickables()

    first_port = 'COM8'
    second_port = 'COM5'
    new_baud_rate = 57 # 19, 38, 57, 115, 230 [kbaud]
    initial_baud_rate = 115200  # 19200 38400, 57600, 115200, 230400 [baud]
    
    change_baud(first_port,second_port,initial_baud_rate,new_baud_rate)

        