import sys
import os
# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import radio_utils.radio_utils as radio_utils
from tests.archived.calculations import average_reports
import tests.archived.testing

# Consts
NUM_OF_PACKAGES = 1024

DEFAULT_PARAMS = tests.archived.testing.DEFAULT_PARAMS

DEFAULT_PACKET_LIST_200B = tests.archived.testing.DEFAULT_PACKET_LIST_200B
DEFAULT_PACKET_LIST_64B = tests.archived.testing.DEFAULT_PACKET_LIST_64B
DEFAULT_PACKET_LIST_16B = tests.archived.testing.DEFAULT_PACKET_LIST_16B

all_packages_concatenated = ''
for i in range(NUM_OF_PACKAGES):
    all_packages_concatenated += DEFAULT_PACKET_LIST_16B[i%len(DEFAULT_PACKET_LIST_16B)].decode()
all_packages_concatenated = tests.archived.testing.str2bin(all_packages_concatenated)

# Force set values (for convenience sake):
DEFAULT_PARAMS['S4:TXPOWER'] = 20
DEFAULT_PARAMS['S2:AIR_SPEED'] = 2
DEFAULT_PARAMS['S10:NUM_CHANNELS'] = 10

def main():
    # serial_port, baud_rate = radio_utils.pick_pickables()
    serial_port = 'COM7'
    baud_rate = 57600
    with radio_utils.RadioModule(serial_port, baud_rate, timeout=0.0001) as receiver:
        receiver.flushInput()      
        receiver.flushOutput()
        all_received_bytes = ""

        # receiver.set_params_to_request(DEFAULT_PARAMS) 

        try:
            while True:
                received_msg = receiver.read_all()
                if not received_msg == b'':
                    print(received_msg.decode('ascii'))
                    all_received_bytes += received_msg.decode('ascii')
                       
        except KeyboardInterrupt:
            print("Stopping receiving.")
        print(f'starts = {all_received_bytes.count("A")} stops = {all_received_bytes.count("O")}')

        all_received_bits = tests.archived.testing.str2bin(all_received_bytes)
        print(f'BER = {tests.archived.testing.calculate_ber(all_packages_concatenated,all_received_bits)}%')



if __name__ == "__main__":
    main()

