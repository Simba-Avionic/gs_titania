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
    "baud_rate": 57600, # max_transmit_speed = min(baud_rate/9.6, air_speed)
    "transmit_rate": 6, # number of messages per second (1 = 500B/s if everything uncommented in send_telemetry)
    "override_rate": 1,  # idk
    "show_received_data": False,
    "set_rtscts": False, # Request to send and clear to send; no idea how to implement it for now
    "target_packets_amount" : 1200 # minimum packages amount to be sent/received
}

CONFIG2 = {
    "port_receiver": "COM5",
    "port_transmitter": "COM5",
    "baud_rate": 57600, # max_transmit_speed = min(baud_rate/9.6, air_speed)
    "transmit_rate": 15, # number of messages per second (1 = 500B/s if everything uncommented in send_telemetry)
    "override_rate": 1,  # idk
    "show_received_data": False,
    "set_rtscts": False, # Request to send and clear to send; no idea how to implement it for now
    "target_packets_amount" : 400 # minimum packages amount to be sent/received
}