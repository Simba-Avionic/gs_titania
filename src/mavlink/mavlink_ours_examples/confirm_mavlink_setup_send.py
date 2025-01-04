from pymavlink import mavutil
import time
# import custom_dialects.custom_dialect

# Initialize MAVLink connection on the transmitting radio
mavlink_sender = mavutil.mavlink_connection('COM7', baud=57600)

# Send data in a loop
try:
    while True:
        mavlink_sender.mav.heartbeat_send(
            mavutil.mavlink.MAV_TYPE_GCS,
            mavutil.mavlink.MAV_AUTOPILOT_INVALID,
            0, 0, 0
        )
        print("Sent heartbeat message")
        time.sleep(1)
except KeyboardInterrupt:
    print("Sender script interrupted. Exiting...")