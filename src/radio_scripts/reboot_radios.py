import sys
import os
# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import radio_utils

if __name__ == '__main__':
    # serial_port, baud_rate = radio_utils.pick_pickables()
    serial_port = 'COM5'
    baud_rate =57600
    transmitter = radio_utils.RadioModule(serial_port, baud_rate)
    receiver = radio_utils.RadioModule('COM7',57600)
    transmitter.enter_command_mode(verbose=True)
    receiver.enter_command_mode(verbose=True)
    # print(transmitter.send_at_command('RTZ'))
    print(receiver.send_at_command('AT&F'))
    print(receiver.send_at_command('AT&W'))
    print(receiver.send_at_command('ATZ'))



    print(transmitter.send_at_command('AT&F'))
    print(transmitter.send_at_command('AT&W'))
    print(transmitter.send_at_command('ATZ'))

    