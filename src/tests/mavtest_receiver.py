from test_config import CONFIG, CONFIG2
import radio_utils.testing.testing as testing



if __name__ == '__main__':
    receiver = testing.MAVTestNode(CONFIG, is_receiver=True)
    receiver.run()