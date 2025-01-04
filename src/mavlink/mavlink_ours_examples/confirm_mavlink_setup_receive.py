from pymavlink import mavutil

# Initialize MAVLink connection on the receiving radio
mavlink_receiver = mavutil.mavlink_connection('COM5', baud=57600)

# Receive data in a loop
try:
    while True:
        msg = mavlink_receiver.recv_match()
        if msg:
            print("Received message:", msg)
except KeyboardInterrupt:
    print("Receiver script interrupted. Exiting...")