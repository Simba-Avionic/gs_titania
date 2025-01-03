import sys
import os
# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import radio_utils.radio_utils as radio_utils


if __name__ == '__main__':
    # serial_port, baud_rate = radio_utils.pick_pickables()
    serial_port1 = 'COM5'
    serial_port2 = 'COM7' # comment out if you want to reboot just one
    baud_rate =57600
    if serial_port2 in locals():
        radio_utils.reboot_radios(serial_port1, baud_rate, serial_port2)
    else:
        radio_utils.reboot_radios(serial_port1, baud_rate)
    
    



    