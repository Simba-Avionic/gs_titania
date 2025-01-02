from test_config import CONFIG, CONFIG_RADIO
import radio_utils.testing.testing as testing
import radio_utils.radio_utils as radio_utils
import time

def run_single_test():
    transmitter = testing.MAVTestNode(CONFIG, is_receiver=False)
    transmitter.run()
    transmitter.close_connection()    


if __name__ == '__main__':

    # Radio parameters setup
    # radio_utils.pick_pickables()
    transmitter = radio_utils.RadioModule(CONFIG["port_transmitter"],CONFIG["baud_rate"])
    transmitter.set_params_to_request(CONFIG_RADIO)
    transmitter.close()

    # Test Execution
    
    run_single_test()
    run_single_test()

    # transmitter.mavlink.close()
    # del transmitter

    