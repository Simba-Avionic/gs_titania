import sys
import os

# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import radio_utils

requested_values = {
    'S0:FORMAT': 25, 
    'S1:SERIAL_SPEED': 115, # 115200
    'S2:AIR_SPEED': 128, 
    'S3:NETID': 18, 
    'S4:TXPOWER': 5, 
    'S5:ECC': 0, 
    'S6:MAVLINK': 0, 
    'S7:OPPRESEND': 0, 
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
    # doesn't work? parameters stay the same
    # serial_port = 'COM7'
    # baud_rate = 115200
    # serial_port2 = 'COM5'
    # baud_rate2 = 115200
    # with radio_utils.RadioModule(serial_port, baud_rate, timeout=1) as ser:  
    #     ser.send_at_command('AT&F') # reset all parameters to factory default
    #     ser.send_at_command('AT&W') # write to eeprom
    #     ser.send_at_command('ATZ') # reboot

    # with radio_utils.RadioModule(serial_port2, baud_rate2, timeout=1) as ser:  
    #     ser.send_at_command('AT&F') # reset all parameters to factory default
    #     ser.send_at_command('AT&W') # write to eeprom
    #     ser.send_at_command('ATZ') # reboot
    # radio_utils.time.sleep(3)

    # serial_port, baud_rate = radio_utils.pick_pickables()
    serial_port = 'COM7'
    baud_rate = 115200
    serial_port2 = 'COM5'
    baud_rate2 = 115200
    transmitter = radio_utils.RadioModule(serial_port, baud_rate)
    receiver = radio_utils.RadioModule(serial_port2, baud_rate2)

    print(transmitter.get_current_parameters())


    transmitter.set_params_to_request(requested_values)
    receiver.set_params_to_request(requested_values)
    transmitter.send_at_command('AT&W')
    receiver.send_at_command('AT&W')
    transmitter.send_at_command('ATO')
    receiver.send_at_command('ATO')
    print(transmitter.get_current_parameters())



    # print(transmitter.get_current_parameters())

        
        

    