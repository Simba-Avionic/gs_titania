import sys
import os
# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import radio_utils


DEFAULT_ECC = 0
DEFAULT_NET_ID = 18
DEFAULT_DUTY_CYCLE = 100
DEFAULT_LBT_RSSI = 0 
DEFAULT_RTSCTS = 0
DEFAULT_MANCHESTER = 0
DEFAULT_MAX_WINDOW = 99

if __name__ == '__main__':
    serial_port, baud_rate = radio_utils.pick_pickables()
    transmitter = radio_utils.RadioModule(serial_port, baud_rate)

    transmitter.enter_command_mode()
    transmitter.set_eec(DEFAULT_ECC)
    transmitter.send_at_command(f'ATS3={DEFAULT_NET_ID}') 
    transmitter.send_at_command(f'ATS11={DEFAULT_DUTY_CYCLE}') 
    transmitter.send_at_command(f'ATS12={DEFAULT_LBT_RSSI}') 
    transmitter.send_at_command(f'ATS13={DEFAULT_MANCHESTER}') 
    transmitter.send_at_command(f'ATS14={DEFAULT_RTSCTS}')
    transmitter.set_mav_link(0) 
    transmitter.send_at_command(f'ATS15={DEFAULT_MAX_WINDOW}')
    transmitter.send_at_command('AT&W') # save to EEPROM

    print(transmitter.get_current_parameters())

    