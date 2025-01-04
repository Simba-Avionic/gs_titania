import sys
import os
# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import radio_utils.testing.testing as testing
import radio_utils.radio_utils as radio_utils
from pymavlink import mavutil
import base64
import time

script_run_with_inputs = len(sys.argv) > 1 

# Handle inputs
if script_run_with_inputs: 
    serial_port = sys.argv[1]
    baud_rate = int(sys.argv[2])
    bandwidth = int(sys.argv[4]) - int(sys.argv[3]) # max_freq - min_freq
    packet_length = int(sys.argv[5]) # [B]
    transmit_speed = int(sys.argv[6])*(packet_length+4)  # packets sent per second times (default packet length + 4 (due to sending shenanigans)) [B]
    air_speed = int(sys.argv[7]) # [kb/s]
    power_tx = int(sys.argv[8]) # [dBm]
    packets_num_to_send = int(sys.argv[9])

# default values
else: 
    # Replace with the receiving radio's serial port and baud rate
    serial_port = "COM5"
    baud_rate = 57600
    packets_num_to_send = 1000 
    packet_length = 10 # 10,20,44 or 50 to choose from [B]

# Initialize MAVLink connection on the receiving radio
mavlink_receiver = mavutil.mavlink_connection(device=serial_port, baud=baud_rate)

# Variables initialization
received_packets = []  # Store received packets to check errors
packet_errors = 0
bit_errors_total = 0
total_bits = 0
currentTime = time.time()

# Test definition
expected_packets = testing.DEFAULT_PACKET_LISTS[packet_length]  # list of expected packets
test_results_file_name = f"baud_{baud_rate}_{packet_length}B_{packets_num_to_send}_packetsSent.csv"


# Execution
try:
    while True:
        message = mavlink_receiver.recv_match(type="STATUSTEXT", blocking=False)
        if message is not None and message.text != '':
            currentTime = time.time()
            pseudo_sleep = 0
            # get sequence number
            start_index = message.text.index('g') + 1
            end_index = start_index + 3  # Adjust for 3-character hex sequence
            sequence_hex = message.text[start_index:end_index].encode()
            sequence_number = int.from_bytes((base64.b64decode(sequence_hex + b'==')))
            # try:
            #     if sequence_byte[0] != 239: # U+FFFD. This is a special character, also known as the "Replacement character".
            #         sequence_number = sequence_byte[0]  # The sequence number is stored in the first byte
            #     else: 
            #         sequence_number += sequence_number # try to follow with previous sequence number
            # except:
            #     print(f'DUPA BLADA: {sequence_byte}')
            #     continue

            received_payload = message.text[end_index:].encode()  # Capture received payload as bytes
            print(f"Received {sequence_number}: {message.text.encode()} | {received_payload}")  
            received_packets.append(received_payload)

            # Extract sequence number from the payload (the byte after 'g' and before the payload data)
            expected_payload = expected_packets[(sequence_number-1) % (testing.PACKETS_ARRAY_LENGTH-1)] # 1-based -> 0-based

            # Compare received packet with the expected packet
            _, bit_errors = testing.calculate_ber(expected_payload, received_payload)
            if bit_errors > 0:
                print(f'Mismatch: sent: {expected_payload} received: {received_payload}')
                packet_errors += 1
            bit_errors_total += bit_errors

            if sequence_number == packets_num_to_send:
                break
        else: 
            elapsed_time = time.time() - currentTime
            if elapsed_time > 4: # if not receiving anything for t time
                break
        
        rssi_report = mavlink_receiver.recv_match(type='RADIO', blocking=False)
        if rssi_report is not None and rssi_report.text != '':
            print(f'RSSI: {rssi_report.rssi}')


    # Final BER and PER calculations
    amount_diff = packets_num_to_send - len(received_packets)
    if amount_diff != 0:
        print(f"Didn't receive all packages; S: {packets_num_to_send}, R: {len(received_packets)}")
        packet_errors += amount_diff
        bit_errors_total += amount_diff*len(expected_packets[0])*8
    per = packet_errors / packets_num_to_send
    ber = bit_errors_total / (packets_num_to_send*len(expected_packets[0])*8)

    print(f"Packet Error Rate (PER): {per:.4f}")
    print(f"Bit Error Rate (BER): {ber:.4f}")


    if script_run_with_inputs:
        testing.save_results_to_csv(output_file_name=test_results_file_name,
                                    bandwidth_kHz =bandwidth, 
                                    powerTx_dBm = power_tx,
                                    airSpeed_kbs = air_speed,
                                    baudRate_DivBy10 = baud_rate/10,
                                    transmitSpeed_B = transmit_speed,
                                    PER = per,
                                    BER = ber
                                    )
    else:
        testing.save_results_to_csv(output_file_name=test_results_file_name,
                                    baudRate_DivBy10 = baud_rate/10,
                                    PER = per,
                                    BER = ber
                                    )

except KeyboardInterrupt:
    print("Receiver script interrupted. Exiting...")