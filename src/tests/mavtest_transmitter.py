import time
from pymavlink import mavutil

from test_config import CONFIG
import radio_utils.testing.testing as testing

class MAVTestTransmitter:
    def __init__(self, config):
        self.port = config["port_transmitter"]
        self.baud_rate = config["baud_rate"]
        self.transmit_rate = config["transmit_rate"]
        self.override_rate = config["override_rate"]
        self.show_received_data = config["show_received_data"]
        self.set_rtscts = config["set_rtscts"]

        # Initialize connection
        self.transmitter = mavutil.mavlink_connection(self.port, baud=self.baud_rate)
        self.transmitter.port.timeout = 1
        self.transmitter.set_rtscts(self.set_rtscts)

        # Initialize variables
        self.start_time = time.time()
        self.last_transmitter_send = time.time()

        # Initialize stats and threads
        self.transmitter_queue, self.transmitter_thread = testing.thread_mav_receive(self.transmitter)
        self.stats = testing.PacketStats(self.transmitter)

    def send_telemetry(self):
        """Send telemetry packets at a fixed rate."""
        testing.send_mav_telemetry_500B(self.transmitter)
        time.sleep(1 / self.transmit_rate)
        self.stats.module_sent = self.transmitter.mav.total_packets_sent

    def process_received_packets(self):
        """Process received packets from the queue."""
        while not self.transmitter_queue.empty():
            testing.receive_mav_packets(self.transmitter_queue, self.stats, self.show_received_data)

    def run(self):
        """Main loop for MAVLink transmitter testing."""
        # TODO: make the loop bytes_sent dependent if provided input

        last_report = time.time()
        try:
            while True:
                self.send_telemetry()
                self.process_received_packets()

                if time.time() - last_report >= 1.0:
                    print("Transmitter stats: ")
                    print(self.stats)
                    last_report = time.time()
        except KeyboardInterrupt:
            print("Stops Transmitting...")


if __name__ == '__main__':
    mavtest = MAVTestTransmitter(CONFIG)
    mavtest.run()