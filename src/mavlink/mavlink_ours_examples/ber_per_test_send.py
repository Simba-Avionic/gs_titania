from pymavlink import mavutil
import time
import random
import string

# Works properly until 100th packet - assumes that packet_id is two digits so PER gets funky 

# Initialize MAVLink connection on the transmitting radio
mavlink_sender = mavutil.mavlink_connection('COM5', baud=57600)

# Counter for the packets
packet_id = 0

# Function to generate a 50-byte payload with a unique packet ID
def generate_50b_message(packet_id):
    random_data = ''.join(random.choices(string.ascii_letters + string.digits, k=48))
    payload = f"{packet_id:02}{random_data}"  # Packet ID (2 chars) + 48 random chars
    return payload.encode('utf-8')

try:
    while True:
        payload = generate_50b_message(packet_id)
        mavlink_sender.mav.statustext_send( # status have a payload up to 100B
            mavutil.mavlink.MAV_SEVERITY_NOTICE, 
            payload.ljust(50, b'\0')
        )
    
        print(f"Sent packet {packet_id}: {payload}")
        packet_id += 1
        time.sleep(1)  # Adjust the interval as needed
except KeyboardInterrupt:
    print("Sender script interrupted. Exiting...")