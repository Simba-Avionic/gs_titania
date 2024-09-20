import sys
import os
# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import radio_utils
from radio_utils.calculations import average_reports
import radio_utils.testing as t


# Consts
DEFAULT_PARAMS = radio_utils.testing.DEFAULT_PARAMS
AIR_RATES = [64, 96, 128, 192, 250]
POWERS = [1, 2, 5, 8, 11, 14, 17, 20]

# Frame configurations: [frame_size, amount_of_frames, frame_ps, speed]
frame_combinations = {
    "short_fast": [16, 1024, 64, 8*1024],  # 8 kb/s
    "medium_fast": [64, 1024, 64, 32 * 1024],  # 32 kb/s
    "long_fast": [200, 1024, 64, 102 * 1024],  # 102 kb/s
    "short_quick": [16, 128, 8, 1 * 1024],  # 1 kb/s
    "medium_quick": [64, 128, 8, 4 * 1024],  # 4 kb/s
    "long_quick": [200, 128, 8, 12 * 1024],  # 12 kb/s
    "short_slow": [16, 16, 1, 128],  # 128 b/s
    "medium_slow": [64, 16, 1, 512],  # 512 b/s
    "long_slow": [200, 16, 1, 1600],  # 1.6 kb/s
}

# Extract combinations with speeds slower than 2 kb/s
slower_than_2kbps = {k: v for k, v in frame_combinations.items() if v[3] < 2 * 1024}
# Extract combinations with speeds slower than 16 kb/s
slower_than_16kbps = {k: v for k, v in frame_combinations.items() if v[3] < 16 * 1024}
# Extract combinations with speeds slower than 32 kb/s
slower_than_32kbps = {k: v for k, v in frame_combinations.items() if v[3] < 32 * 1024}

def init():
    # serial_port, baud_rate = radio_utils.pick_pickables()
    serial_port = 'COM5'
    baud_rate = 57600
    transmitter = radio_utils.RadioModule(serial_port, baud_rate,timeout=0.0001)
    transmitter.reset_input_buffer()      
    transmitter.reset_output_buffer()
    # transmitter.set_params_to_request(DEFAULT_PARAMS) # can comment it out to save some time if already set ---> best/easiest way to edit params
    # print(transmitter.get_current_parameters()) # can comment it out to save some time
    # print(transmitter.get_current_parameters(remote=True)) # can comment it out to save some time
    return transmitter

def run_test(transmitter:radio_utils.RadioModule, power_list, air_rate_list, X_speed = 0, Y_speed = 0):
    # x_speed - air rate at which bandwidth not required to be higher than 2kbps
    # y_speed - air rate at which bandwidth not required to be higher than 16kbps
    for tx_p in power_list:
        transmitter.set_transmit_power(tx_p)
        for air_spd in air_rate_list:
            transmitter.set_air_rate(air_spd)
            if air_spd == X_speed:
                size_amount_speed_list = [[value[0], value[1], value[2]] for value in slower_than_2kbps.values()]
            elif air_spd == Y_speed:
                size_amount_speed_list = [[value[0], value[1], value[2]] for value in slower_than_16kbps.values()]
            else:
                size_amount_speed_list = [[value[0], value[1], value[2]] for value in frame_combinations.values()]
            for size_amount_speed in size_amount_speed_list:
                packets_to_send = eval(f't.DEFAULT_PACKET_LIST_{size_amount_speed[0]}B')
                current_inputs_str = (f'AIR_SPD={air_spd}; TX_P={tx_p}; PACKET_SIZE={size_amount_speed[0]}B; PACKET_AMOUNT={size_amount_speed[1]}; PACKET_SPEED={size_amount_speed[2]}')
                print(current_inputs_str)
                t.send_packets_at_defined_speed(transmitter=transmitter,
                                                predefined_packets=packets_to_send,
                                                number_of_packets_to_send=size_amount_speed[1],speed=size_amount_speed[2])
                
                transmitter.write('f'.encode())
                transmitter.write(('a'+current_inputs_str +'o').encode()) 
                transmitter.write(('a'+current_inputs_str +'o').encode()) 
                radio_utils.time.sleep(3) # give some time to write results on receiver end
                transmitter.reset_input_buffer()      
                transmitter.reset_output_buffer()

                while True:
                    # print(transmitter.read())
                    if transmitter.read() == b'K':
                        break


            transmitter.read_all()
            transmitter.reset_input_buffer()      
            transmitter.reset_output_buffer()
            
    
def test_R_01(transmitter:radio_utils.RadioModule):
    run_test(transmitter, power_list=[20], air_rate_list=[2], X_speed = 2, Y_speed = 16)
    # run_test(transmitter, power_list=[20,17,11,1], air_rate_list=[2,16,64,250], X_speed = 2, Y_speed = 16)
def test_R_02(transmitter:radio_utils.RadioModule):
    run_test(transmitter, power_list=[20,17,11,1], air_rate_list=[16,64,250], Y_speed = 16)


def main():
    transmitter = init()
    test_R_01(transmitter)


if __name__ == "__main__":
    main()

