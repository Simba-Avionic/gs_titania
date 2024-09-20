import sys
import os

# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import radio_utils

requested_values = {
    'S0:FORMAT': 25, 
    'S1:SERIAL_SPEED': 57, 
    'S2:AIR_SPEED': 64, 
    'S3:NETID': 18, 
    'S4:TXPOWER': 20, 
    'S5:ECC': 0, 
    'S6:MAVLINK': 0, 
    'S7:OPPRESEND': 1, 
    'S8:MIN_FREQ': 434550, 
    'S9:MAX_FREQ': 434650, 
    'S10:NUM_CHANNELS': 10, 
    'S11:DUTY_CYCLE': 100, 
    'S12:LBT_RSSI': 0, 
    'S13:MANCHESTER': 0, 
    'S14:RTSCTS': 0, 
    'S15:MAX_WINDOW': 131
}

if __name__ == '__main__':
    # serial_port, baud_rate = radio_utils.pick_pickables()
    serial_port = 'COM7'
    baud_rate = 57600
    transmitter = radio_utils.RadioModule(serial_port, baud_rate)
    transmitter.set_params_to_request(requested_values)
    transmitter.send_at_command('AT&W')
    print(transmitter.get_current_parameters())

        
        

    