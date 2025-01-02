from test_config import CONFIG, CONFIG_RADIO
import radio_utils.testing.testing as testing
import radio_utils.radio_utils as radio_utils



if __name__ == '__main__':
    # Radio parameters setup
    receiver = radio_utils.RadioModule(CONFIG["port_receiver"],CONFIG["baud_rate"])
    receiver.set_params_to_request(CONFIG_RADIO)
    receiver.close()

    receiver = testing.MAVTestNode(CONFIG, is_receiver=True)
    receiver.run()