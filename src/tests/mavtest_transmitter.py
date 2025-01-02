from test_config import CONFIG
import radio_utils.testing.testing as testing


if __name__ == '__main__':
    transmitter = testing.MAVTestNode(CONFIG, is_receiver=False)
    transmitter.run()