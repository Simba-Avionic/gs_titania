import random
import string
from pymavlink import mavutil
import time
# import custom_dialects.custom_dialect

# Initialize MAVLink connection on the transmitting radio
mavlink_sender = mavutil.mavlink_connection('COM5', baud=57600,dialect='custom_dialect')

# Function to generate a 50-byte payload with a unique packet ID
def generate_50b_message():
    payload = ''.join(random.choices(string.ascii_letters + string.digits, k=50))
    return payload.encode('utf-8')

# Send data in a loop

try:
    packet_id = 0
    while True:
        payload = generate_50b_message()
        mavlink_sender.mav.test_payload_send( 
            packet_id, 
            payload
        )

        print(f"Sent packet {packet_id}: {payload}")
        packet_id += 1
        time.sleep(1)  # Adjust the interval as needed
except KeyboardInterrupt:
    print("Sender script interrupted. Exiting...")