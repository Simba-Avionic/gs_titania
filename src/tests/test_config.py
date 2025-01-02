# test_config.py
import sys, os
# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

'''uncomment if you want to check available serial ports and baud rate'''
# import radio_utils.radio_utils as radio_utils
# radio_utils.pick_pickables() 

CONFIG = {
    "port_receiver": "COM7",
    "port_transmitter": "COM5",
    "baud_rate": 57600, # max_transmit_speed = min(baud_rate/9.6, air_speed)
    "transmit_rate": 6, # number of messages per second (1 = 500B/s if everything uncommented in send_telemetry)
    "override_rate": 1,  # idk
    "show_received_data": False,
    "set_rtscts": False, # Request to send and clear to send; no idea how to implement it for now
    "target_packets_amount" : 400 # minimum packages amount to be sent/received
}

CONFIG_RADIO = {
    # 'S0:FORMAT': 26, 
    #'S1:SERIAL_SPEED': 57, 
    'S2:AIR_SPEED': 64, 
    'S3:NETID': 25, 
    'S4:TXPOWER': 20, 
    'S5:ECC': 0, 
    'S6:MAVLINK': 1, 
    'S7:OPPRESEND': 0, 
    'S8:MIN_FREQ': 433070, # Default value; can be overridden
    'S9:MAX_FREQ': 434790,  # Default value; can be overridden
    'S10:NUM_CHANNELS': 10, 
    'S11:DUTY_CYCLE': 100, 
    'S12:LBT_RSSI': 0, 
    'S13:MANCHESTER': 0, 
    'S14:RTSCTS': 0, 
    'S15:MAX_WINDOW': 131

}

CONFIG2 = {
    "port_receiver": "COM5",
    "port_transmitter": "COM5",
    "baud_rate": 57600, # max_transmit_speed = min(baud_rate/9.6, air_speed)
    "transmit_rate": 15, # number of messages per second (1 = 500B/s if everything uncommented in send_telemetry)
    "override_rate": 2,  # idk
    "show_received_data": False,
    "set_rtscts": False, # Request to send and clear to send; no idea how to implement it for now
    "target_packets_amount" : 400 # minimum packages amount to be sent/received
}