import time
from pymavlink import mavutil

from test_config import CONFIG
import radio_utils.testing.testing as testing

class MAVTestReceiver:
    def __init__(self, config):
        self.port = config["port_receiver"]
        self.baud_rate = config["baud_rate"]
        self.transmit_rate = config["transmit_rate"]
        self.override_rate = config["override_rate"]
        self.show_received_data = config["show_received_data"]
        self.set_rtscts = config["set_rtscts"]

        # Initialize connection
        self.receiver = mavutil.mavlink_connection(self.port, baud=self.baud_rate)
        self.receiver.port.timeout = 0.0001
        self.receiver.set_rtscts(self.set_rtscts)

        # Initialize variables
        self.start_time = time.time()
        self.last_receiver_send = time.time()
        self.last_override_send = time.time()

        # Initialize stats and threads
        self.receiver_queue, self.receiver_thread = testing.thread_mav_receive(self.receiver)
        self.stats = testing.PacketStats(self.receiver)

    def send_heartbeat(self):
        """Send GCS (receiver) heartbeat messages."""
        now = time.time()
        if now - self.last_receiver_send < 1.0:
            return
        self.receiver.mav.heartbeat_send(1, 6, 0, 0, 0, 0)
        self.last_receiver_send = now

    def send_override(self):
        """Send RC_CHANNELS_OVERRIDE messages from GCS (receiver)."""
        now = time.time()
        if self.override_rate == 0 or now - self.last_override_send < 1.0 / self.override_rate:
            return
        time_ms = int((now - self.start_time) * 1.0e3)
        time_ms_low = time_ms % 65536
        time_ms_high = (time_ms - time_ms_low) // 65536
        self.receiver.mav.rc_channels_override_send(1, 2, time_ms_low, time_ms_high, 0, 0, 0, 0, 0, 0)
        self.last_override_send = now

    def run(self):
        """Main loop for MAVLink testing."""
        # TODO: make the loop bytes_received dependent if provided input
        last_report = time.time()
        try:
            while True:
                self.send_heartbeat()
                self.send_override()
                self.stats.module_sent = self.receiver.mav.total_packets_sent

                while not self.receiver_queue.empty():
                    testing.receive_mav_packets(self.receiver_queue, self.stats, self.show_received_data)

                if time.time() - last_report >= 1.0:
                    print("Receiver stats: ")
                    print(self.stats)
                    last_report = time.time()
        except KeyboardInterrupt:
            print("Stops Receiving...")


if __name__ == '__main__':
    mavtest = MAVTestReceiver(CONFIG)
    mavtest.run()