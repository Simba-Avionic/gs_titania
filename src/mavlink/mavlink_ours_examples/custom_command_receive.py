from pymavlink import mavutil

# Works properly until 100th packet - assumes that packet_id is two digits so PER gets funky 

# Initialize MAVLink connection on the receiving radio
mavlink_receiver = mavutil.mavlink_connection('COM7', baud=57600)

# Counters for BER and PER
total_bits = 0
bit_errors = 0
total_packets = 0
packet_errors = 0
expected_packet_id = 0

def calculate_bit_errors(sent, received):
    return sum(1 for s, r in zip(sent, received) if s != r)

while True:
    msg = mavlink_receiver.recv_match(type='TESTPAYLOAD', blocking=False) 
    print(msg)

    msg = mavlink_receiver.recv_match(type='TEST_PAYLOAD', blocking=False) 
    
    print(mavlink_receiver.messages)
    print(msg)

    msg = mavlink_receiver.recv_match()
    print(msg)


    # ??????? honestly don't know
