# test_config.py
import sys, os
# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

'''uncomment and run if you want to check available serial ports and baud rate'''
# import radio_utils.radio_utils as radio_utils
# radio_utils.pick_pickables() 


DEFAULT_CONFIG = {
    "port_receiver": "COM7",
    "port_transmitter": "COM5",
    "baud_rate": 57600, # max_transmit_speed = min(baud_rate/9.6, air_speed)
    "transmit_rate": 2, # number of messages per second (1 = 500B/s if everything uncommented in send_telemetry)
    "override_rate": 1,  # idk
    "show_received_data": False,
    "set_rtscts": False, # Request to send and clear to send; no idea how to implement it for now
    "target_packets_amount" : 300 # minimum packages amount to be sent/received (real target is multiplied by (transmit rate * 0.8))
}

DEFAULT_CONFIG_RADIO = {
    # 'S0:FORMAT': 26, 
    'S1:SERIAL_SPEED': 57, 
    'S2:AIR_SPEED': 192, 
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

# ~130 * 20s each subtests ----> 43 min?

# Test1: airspeed variation (~35 subtests)
TEST_1_AIRSPEEDS = [32, 48, 64, 96, 128, 192, 250] 
TEST_1_TRANSMIT_RATES = [1,4,8,12,15] 

# Test2: bandwidth variation (~30)
TEST_2_MAX_FREQ = [433080, 433170, 433270, 433570, 433870, 434070] # 6
TEST_2_TRANSMIT_RATES = [1,4,8,12,15] # 5

# Test3: baud rate variation # 60
TEST_3_BAUD_RATE = [19200, 38400, 57600, 115200, 230400] 
TEST_3_SERIAL_SPEED = [19, 38, 57, 115, 230]
TEST_3_TRANSMIT_RATES = [1,2,4,8,12,16,20,24,28,36,42,46] 

# Test4: num of channels variation # 15
TEST_4_NUM_CHANNELS = [5,10,20,30,42] 
TEST_4_TRANSMIT_RATES = [1,8,15]

# Test5: duty cycle variation # 9
TEST_5_DUTY_CYCLE = [100,60,30]
TEST_5_TRANSMIT_RATES = [1,8,15]
