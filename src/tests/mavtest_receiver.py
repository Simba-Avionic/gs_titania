from test_config import DEFAULT_CONFIG, DEFAULT_CONFIG_RADIO, TEST_1_AIRSPEEDS, TEST_1_TRANSMIT_RATES
import radio_utils.testing.testing as testing
import radio_utils.radio_utils as radio_utils
import time


def write_temp_to_csv(receiver:radio_utils.RadioModule):
    whole_report = receiver.get_output_data()
    csv_name = f"test_baud_{DEFAULT_CONFIG["baud_rate"]}_receiver.csv"
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

def run_test():
    # Test exec
    receiver = testing.MAVTestNode(DEFAULT_CONFIG,DEFAULT_CONFIG_RADIO,is_receiver=True)
    print(f"TRANSMIT RATE: {DEFAULT_CONFIG["transmit_rate"]}")
    receiver.run()
    receiver.close_connection()
    time.sleep(1)

def test_1(): # airspeeds and transmit rates changing, constant power, constant bandwidth

    for air_speed in TEST_1_AIRSPEEDS:
        # setup
        receiver = radio_utils.RadioModule(DEFAULT_CONFIG["port_receiver"],DEFAULT_CONFIG["baud_rate"])
        
        DEFAULT_CONFIG_RADIO['S2:AIR_SPEED'] = air_speed
        receiver.set_params_to_request(DEFAULT_CONFIG_RADIO)
        write_temp_to_csv(receiver)
        receiver.leave_command_mode()
        receiver.close()
        time.sleep(1)
        # exec
        for transmit_rate in TEST_1_TRANSMIT_RATES:
            DEFAULT_CONFIG["transmit_rate"] = transmit_rate
            run_test()
            # finish
            input("Click enter to continue (receiver/transmitter ready for next subtest)")

if __name__ == '__main__':
    # Radio parameters setup
    test_1()

    