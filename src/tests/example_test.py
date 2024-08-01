import sys
import os
# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import radio_utils
from radio_utils.calculations import average_reports
import radio_utils.testing

## oba radia podłączone do tego samego urządzenia; wpływ wariacji mocy na resztę parametrów ##

# Constants
SEND_PORT = 'COM5' # '/dev/ttyUSB0'  # Serial port for sending radio
RECEIVE_PORT = 'COM6' # '/dev/ttyUSB1'  # Serial port for receiving radio
BAUDRATE = 57600  # Baud rate for SiK radios

MESSAGE = 'Pan Szczekoscisk!'  # Message to send
INTERVAL = 1  # Interval between sends in seconds
FILEPATH = os.path.dirname(__file__)


def send_message(serial_port, message):
    """Send a message through the serial port."""
    serial_port.write((message + '\r\n').encode())

def main():
    # Open serial connections
    transmitter = radio_utils.RadioModule(SEND_PORT, BAUDRATE)
    receiver = radio_utils.RadioModule(RECEIVE_PORT, BAUDRATE)
    print("Transmitter radio parameters:")
    print(transmitter.get_current_parameters())
    print("Receiver radio parameters:")
    print(receiver.get_current_parameters())
    
    results = []

    try:
        for power in range(1,21):
            if transmitter.set_transmit_power(power):
                radio_utils.time.sleep(1) # guard
                rssi_report_array = []
                for t in range(1,4): 
                    # Send message
                    send_message(transmitter, MESSAGE)
                    print(f"Sent: {MESSAGE}")
                    
                    # Get telemetry data from receiving radio
                    tdm_report, rssi_report = receiver.get_output_data()
                    if tdm_report and rssi_report is not None:
                        print(f"{tdm_report}\n{rssi_report}")
                        rssi_report_array.append(rssi_report)
                    else:
                        print("Failed to extract reports.")
                results_temp_dict = {'txPower' : power}
                results_temp_dict.update(average_reports(rssi_report_array))

                results.append(results_temp_dict)
                # Wait before sending the next message
                # radio_utils.time.sleep(INTERVAL)
    except KeyboardInterrupt:
        print("Stopping transmission.")

    radio_utils.testing.write_results_to_csv(results,f'{FILEPATH}/results_power_var.csv')
if __name__ == "__main__":
    main()