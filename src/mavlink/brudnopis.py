from pymavlink import mavutil
# import pymavlink.dialects.v20.minimal # <---- dialekty można w ten sposób znaleźć
import sys
import os
# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import radio_utils

# podobno firmware wspiera oba formaty mavlinku (1.0, 2.0)
# mission planner też nie jest w stanie się połączyć i krzyczy o brak heart beatu --> heartbeat jest wysyłany przez autopilota nie przez radia

# # port,baud = radio_utils.pick_pickables()
connection = mavutil.mavlink_connection('COM5',115200)
# connection.write(b'dupa') # ważne żeby encodować jeśli się wysyła czysto wiadomości 

# connection.mav.param_request_list_send( # <--- jeden z problemów jak ogarnąć idsy
#     18, 18
# )
# print(f'{connection.target_system}, {connection.target_component}')

# Listen for a heartbeat message to identify the system ID
# heartbeat_msg = connection.recv_match(type='HEARTBEAT', blocking=True)
while True:
    msg = connection.recv_msg()
    if msg:
        print(msg)
    time.sleep(0.1)


# Print out the system ID from the HEARTBEAT message
print("Local system ID:", heartbeat_msg.get_srcSystem())

# while True:
#     try:
#         message = connection.recv_match(type='PARAM_VALUE', blocking=True).to_dict()
#         print('name: %s\tvalue: %d' % (message['param_id'], message['param_value']))
#     except Exception as error:
#         print(error)
#         sys.exit(0)





