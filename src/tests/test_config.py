# test_config.py
import sys, os
# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

'''uncomment if you want to check available serial ports and baud rate'''
# import radio_utils.radio_utils as radio_utils
# radio_utils.pick_pickables() 

CONFIG = {
    "port_receiver": "COM8",
    "port_transmitter": "COM5",
    "baud_rate": 57600,
    "transmit_rate": 15, # max_transmit_speed = min(baud_rate/9.6, air_speed)
    "override_rate": 1,  # number of messages per second (1 = 500B/s if everything uncommented in send_telemetry)
    "show_received_data": False,
    "set_rtscts": False
}