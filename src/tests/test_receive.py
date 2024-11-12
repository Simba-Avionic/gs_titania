import sys
import os
# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import radio_utils.testing.testing as testing
import radio_utils.radio_utils as radio_utils
from pymavlink import mavutil
import base64
import time

# Replace with the receiving radio's serial port and baud rate
serial_port = "COM7"
baud_rate = 57600

# Initialize MAVLink connection on the receiving radio
mavlink_receiver = mavutil.mavlink_connection(device=serial_port, baud=baud_rate)

expected_packets = testing.DEFAULT_PACKET_LIST_10B  # List of expected packets
messages_amount = testing.TestLength.LONG.value


received_packets = []  # Store received packets to check errors

packet_errors = 0
bit_errors_total = 0
total_bits = 0
currentTime = time.time()


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
            print(f"Received {sequence_number}: {message.text.encode()} | {received_payload}")  # Corrected indexing
            received_packets.append(received_payload)

            # Extract sequence number from the payload (the byte after 'g' and before the payload data)

            expected_payload = expected_packets[(sequence_number-1) % (testing.PACKETS_ARRAY_LENGTH-1)] # sequence starts with one

            # Compare received packet with the expected packet
            _, bit_errors = testing.calculate_ber(expected_payload, received_payload)
            if bit_errors > 0:
                print(f'Mismatch: sent: {expected_payload} received: {received_payload}')
                packet_errors += 1
            bit_errors_total += bit_errors

            if sequence_number == messages_amount:
                break
        else:
            elapsed_time = time.time() - currentTime
            if elapsed_time > 4:
                break

    # Final BER and PER calculations
    amount_diff = messages_amount - len(received_packets)
    if amount_diff != 0:
        print(f"Didn't receive all packages; S: {messages_amount}, R: {len(received_packets)}")
        packet_errors += amount_diff
        bit_errors_total += amount_diff*len(expected_packets[0])*8
    per = packet_errors / messages_amount
    ber = bit_errors_total / (messages_amount*len(expected_packets[0])*8)

    print(f"Packet Error Rate (PER): {per:.4f}")
    print(f"Bit Error Rate (BER): {ber:.4f}")

    output_filename = 'speeds.txt'
    with open(output_filename, 'a') as file:
    # Write a header for clarity (optional)
        file.write(f"Packet Error Rate (PER): {per:.4} ")
        file.write(f"Bit Error Rate (BER): {ber:.4f}\n")

except KeyboardInterrupt:
    print("Receiver script interrupted. Exiting...")