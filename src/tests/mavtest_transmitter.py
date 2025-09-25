from test_config import DEFAULT_CONFIG, DEFAULT_CONFIG_RADIO, TEST_1_AIRSPEEDS, TEST_1_TRANSMIT_RATES
from test_config import TEST_2_MAX_FREQ, TEST_2_TRANSMIT_RATES
from test_config import TEST_3_BAUD_RATE, TEST_3_SERIAL_SPEED, TEST_3_TRANSMIT_RATES
from test_config import TEST_4_NUM_CHANNELS, TEST_4_TRANSMIT_RATES
from test_config import TEST_5_DUTY_CYCLE, TEST_5_TRANSMIT_RATES

import radio_utils.testing.testing as testing
import radio_utils.radio_utils as radio_utils
import time, math
from radio_scripts.change_baud import change_baud


def run_test():
    # Test exec
    receiver = testing.MAVTestNode(DEFAULT_CONFIG,DEFAULT_CONFIG_RADIO, is_receiver=False)
    receiver.run()
    receiver.close_connection()
    time.sleep(0.5)

def change_baud_wrapper(initial_buad_rate,new_baud_rate):
        if initial_buad_rate == None or 0:
            initial_buad_rate = radio_utils.detect_baud_rate(DEFAULT_CONFIG["port_transmitter"])
            if new_baud_rate == math.floor(initial_buad_rate/1000):
                print("already set to target baud rate")
                return
            change_baud(first_port=DEFAULT_CONFIG["port_transmitter"],initial_baud_rate=initial_buad_rate,new_baud_rate=new_baud_rate)
        elif not change_baud(first_port=DEFAULT_CONFIG["port_transmitter"],initial_baud_rate=initial_buad_rate,new_baud_rate=new_baud_rate):
            initial_buad_rate = radio_utils.detect_baud_rate(DEFAULT_CONFIG["port_transmitter"])
            change_baud(first_port=DEFAULT_CONFIG["port_transmitter"],initial_baud_rate=initial_buad_rate,new_baud_rate=new_baud_rate)

def write_temp_to_csv(transmitter:radio_utils.RadioModule):
    whole_report = transmitter.get_output_data()
    if whole_report['temperature'] == -276: # try again
        whole_report = transmitter.get_output_data()
    csv_name = f"test_baud_{DEFAULT_CONFIG['baud_rate']}_transmitter.csv"
    testing.save_results_to_csv(csv_name,
                        POWER =DEFAULT_CONFIG_RADIO["S4:TXPOWER"],
                        BANDWIDTH = DEFAULT_CONFIG_RADIO["S9:MAX_FREQ"] - DEFAULT_CONFIG_RADIO["S8:MIN_FREQ"],
                        AIR_SPEED = DEFAULT_CONFIG_RADIO["S2:AIR_SPEED"],
                        TRANSMIT_RATE = DEFAULT_CONFIG["transmit_rate"],
                        BAUD_RATE = DEFAULT_CONFIG["baud_rate"],
                        L_RSSI = whole_report['L_RSSI'],
                        R_RSSI = whole_report['R_RSSI'],
                        L_NOISE = whole_report['L_noise'],
                        R_NOISE = whole_report['R_noise'],
                        PACKETS_LOST_TOTAL = 0,
                        PER = 0,
                        TEMPERATURE = whole_report['temperature']
                        )

def test_1(): # airspeeds and transmit rates changing, constant power, constant bandwidth

    for air_speed in TEST_1_AIRSPEEDS:
        # setup
        transmitter = radio_utils.RadioModule(DEFAULT_CONFIG["port_transmitter"],DEFAULT_CONFIG["baud_rate"])
        DEFAULT_CONFIG_RADIO['S2:AIR_SPEED'] = air_speed
        transmitter.set_params_to_request(DEFAULT_CONFIG_RADIO)
        write_temp_to_csv(transmitter)
        transmitter.leave_command_mode()
        transmitter.close()
        time.sleep(1)
        # exec
        for transmit_rate in TEST_1_TRANSMIT_RATES:
            if transmit_rate*500 > DEFAULT_CONFIG["baud_rate"]/9.6 or transmit_rate*500 > air_speed*1000/8 * 1.5:
                continue # max transmit speed is baud_rate/9.6 B/s
            DEFAULT_CONFIG["transmit_rate"] = transmit_rate
            run_test()
            # finish
            input("Click enter to continue (receiver/transmitter ready for next subtest)")

def test_2(): # bandwidth and transmit rates changing, constant power, constant air speed
    for max_freq in TEST_2_MAX_FREQ:
        # setup
        transmitter = radio_utils.RadioModule(DEFAULT_CONFIG["port_transmitter"],DEFAULT_CONFIG["baud_rate"])
        DEFAULT_CONFIG_RADIO['S9:MAX_FREQ'] = max_freq
        transmitter.set_params_to_request(DEFAULT_CONFIG_RADIO)
        write_temp_to_csv(transmitter)
        transmitter.leave_command_mode()
        transmitter.close()
        time.sleep(1)
        # exec
        for transmit_rate in TEST_2_TRANSMIT_RATES:
            if transmit_rate*500 > DEFAULT_CONFIG["baud_rate"]/9.6:
                continue # max transmit speed is baud_rate/9.6 B/s 
            DEFAULT_CONFIG["transmit_rate"] = transmit_rate
            run_test()
            # finish
            input("Click enter to continue (receiver/transmitter ready for next subtest)")

def test_3(): # baud and transmit rates changing

    new_baud_rate=TEST_3_SERIAL_SPEED[0]
    initial_buad_rate = DEFAULT_CONFIG["baud_rate"]
    change_baud_wrapper(initial_buad_rate,new_baud_rate)
    first_subtest = True
    for i in range(len(TEST_3_BAUD_RATE)):

        if first_subtest:
            transmitter = radio_utils.RadioModule(DEFAULT_CONFIG["port_transmitter"],TEST_3_BAUD_RATE[0])
            transmitter.set_params_to_request(DEFAULT_CONFIG_RADIO)
            first_subtest = False
        else:
            change_baud_wrapper(TEST_3_BAUD_RATE[i-1],TEST_3_SERIAL_SPEED[i])
            transmitter =radio_utils.RadioModule(DEFAULT_CONFIG["port_transmitter"],TEST_3_BAUD_RATE[i])            
        # setup
        DEFAULT_CONFIG["baud_rate"] = TEST_3_BAUD_RATE[i]
        write_temp_to_csv(transmitter)
        transmitter.leave_command_mode()
        transmitter.close()
        time.sleep(1)
        # exec
        for transmit_rate in TEST_3_TRANSMIT_RATES:
            if transmit_rate*500 > TEST_3_BAUD_RATE[i]/9.6:
                continue # max transmit speed is baud_rate/9.6 B/s 
            DEFAULT_CONFIG["transmit_rate"] = transmit_rate
            run_test()
            # finish
            input("Click enter to continue (receiver/transmitter ready for next subtest)")

def test_4(): # % of duty_cycle changing
    for duty_cycle in TEST_5_DUTY_CYCLE:
        # setup
        transmitter = radio_utils.RadioModule(DEFAULT_CONFIG["port_transmitter"],DEFAULT_CONFIG["baud_rate"])
        DEFAULT_CONFIG_RADIO['S11:DUTY_CYCLE'] = duty_cycle
        transmitter.set_params_to_request(DEFAULT_CONFIG_RADIO)
        write_temp_to_csv(transmitter)
        transmitter.leave_command_mode()
        transmitter.close()
        time.sleep(1)
        # exec
        for transmit_rate in TEST_5_TRANSMIT_RATES:
            if transmit_rate*500 > DEFAULT_CONFIG["baud_rate"]/9.6:
                continue # max transmit speed is baud_rate/9.6 B/s 
            DEFAULT_CONFIG["transmit_rate"] = transmit_rate
            run_test()
            # finish
            input("Click enter to continue (receiver/transmitter ready for next subtest)")

def test_5(): # duty cycle changing
    for num_channels in TEST_4_NUM_CHANNELS:
        # setup
        transmitter = radio_utils.RadioModule(DEFAULT_CONFIG["port_transmitter"],DEFAULT_CONFIG["baud_rate"])
        DEFAULT_CONFIG_RADIO['S10:NUM_CHANNELS'] = num_channels
        transmitter.set_params_to_request(DEFAULT_CONFIG_RADIO)
        write_temp_to_csv(transmitter)
        transmitter.leave_command_mode()
        transmitter.close()
        time.sleep(1)
        # exec
        for transmit_rate in TEST_4_TRANSMIT_RATES:
            if transmit_rate*500 > DEFAULT_CONFIG["baud_rate"]/9.6:
                continue # max transmit speed is baud_rate/9.6 B/s 
            DEFAULT_CONFIG["transmit_rate"] = transmit_rate
            run_test()
            # finish
            input("Click enter to continue (receiver/transmitter ready for next subtest)")

def test_6(): # do bawienia sie, dluuuugie nadawanie i odbieranie
    # setup
    transmitter = radio_utils.RadioModule(DEFAULT_CONFIG["port_transmitter"],DEFAULT_CONFIG["baud_rate"])
    transmitter.set_params_to_request(DEFAULT_CONFIG_RADIO)
    DEFAULT_CONFIG["target_packets_amount"] = 40000000000
    write_temp_to_csv(transmitter)
    transmitter.leave_command_mode()
    transmitter.close()
    time.sleep(1)

    run_test()

# powinienem był minimalnie inaczej ogarnąć te default configi, odpalaj maks jeden test_x na run 
if __name__ == '__main__':
    # change_baud_wrapper(None,57) # run if baud rate got broken
    # radio_utils.reboot_radios(DEFAULT_CONFIG['port_transmitter'],57600) # run if you hope that reset to default will do miracles
    
    test_1()
    # test_2() # ten dziad
    # test_3()
    # test_4() # i ten dziad
    # test_5()
    # test_6()


    