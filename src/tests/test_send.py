import sys
import os
# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import radio_utils.testing.testing as testing
import radio_utils.radio_utils as radio_utils

from pymavlink import mavutil
import time
import base64


# serial_port, baud_rate = radio_utils.pick_pickables()
serial_port = "COM5"
baud_rate = 57600

if len(sys.argv) > 1:
    sending_freq = int(sys.argv[1])
    
else:
    sending_freq = 10

# Initialize MAVLink connection on the transmitting radio
mavlink_sender = mavutil.mavlink_connection(device=serial_port, baud=baud_rate)

# Counter for the packets
packet_id = 0



try:
    payload = testing.DEFAULT_PACKET_LIST_10B
    for i in range(testing.TestLength.LONG.value):
        # Loop over the hardcoded packet list and get the payload
        subtest_payload = payload[i % (testing.PACKETS_ARRAY_LENGTH - 1)]

        # Encode the sequence number in base64 without padding
        sequence_encoded = base64.b64encode((i+1).to_bytes(2, 'big')).rstrip(b'=') # max 64x64x64 = 262143 sequences
        # Ensure it's two characters for consistency
        if len(sequence_encoded) == 1:
            sequence_encoded = b'0' + sequence_encoded

        # Add 'g' and sequence number at the beginning
        modified_payload = b'g' + sequence_encoded + subtest_payload # \x00 is considered null terminator for this type of message hence b64

        # Send the modified payload
        mavlink_sender.mav.statustext_send(
            mavutil.mavlink.MAV_SEVERITY_NOTICE, 
            modified_payload+modified_payload
        )
        
        print(f"Sent {len(modified_payload)}B packet no: {i + 1}: {modified_payload} \t|\t {subtest_payload}")
        time.sleep(1/sending_freq)  # Adjust the interval as needed
    output_filename = 'speeds.txt'
    with open(output_filename, 'a') as file:
        # Write a header for clarity (optional)
        file.write(f"Speed: {10*sending_freq}B/s ")


except KeyboardInterrupt:
    print("Sender script interrupted. Exiting...")