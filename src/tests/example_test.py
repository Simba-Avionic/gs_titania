import sys
import os
# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import radio_utils
import csv
from radio_utils.calculations import average_reports

## oba radia podłączone do tego samego urządzenia; wpływ wariacji mocy na resztę parametrów ##

# Constants
SEND_PORT = 'COM5' # '/dev/ttyUSB0'  # Serial port for sending radio
RECEIVE_PORT = 'COM6' # '/dev/ttyUSB1'  # Serial port for receiving radio
BAUDRATE = 57600  # Baud rate for SiK radios

MESSAGE = 'Pan Szczekoscisk!'  # Message to send
INTERVAL = 1  # Interval between sends in seconds
FREQUENCY = 434550  # Frequency in Hz (adjust for your specific SiK radio frequency)
FILEPATH = os.path.dirname(__file__)


def send_message(serial_port, message):
    """Send a message through the serial port."""
    serial_port.write((message + '\r\n').encode())

def write_results_to_csv(results,filename):
    keys = results[0].keys()
    with open(filename, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(results)

def main():
    # Open serial connections
    send_radio = radio_utils.RadioModule(SEND_PORT, BAUDRATE)
    receive_radio = radio_utils.RadioModule(RECEIVE_PORT, BAUDRATE)
    print("Transmitter radio parameters:")
    print(send_radio.get_current_parameters())
    print("Receiver radio parameters:")
    print(receive_radio.get_current_parameters())
    
    results = []

    try:
        for power in range(1,21):
            if send_radio.set_transmit_power(power):
                radio_utils.time.sleep(1) # guard
                rssi_report_array = []
                for t in range(1,4): # potencjalnie wzięcie kilku próbek i późniejszego uśrednienia
                    # Send message
                    send_message(send_radio, MESSAGE)
                    print(f"Sent: {MESSAGE}")
                    
                    # Get telemetry data from receiving radio
                    tdm_report, rssi_report = receive_radio.get_output_data()
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

    write_results_to_csv(results,f'{FILEPATH}/results_power_var.csv')
if __name__ == "__main__":
    main()