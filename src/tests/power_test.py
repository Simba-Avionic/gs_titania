import sys
import os
# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import radio_utils
from radio_utils.calculations import average_reports
import radio_utils.testing

# Tests the effect of changing transmitter power 

MESSAGE = 'Pan Szczekoscisk!'  # Message to send
INTERVAL = 1  # Interval between sends in seconds
FILEPATH = os.path.dirname(__file__)


def send_message(serial_port, message):
    """Send a message through the serial port."""
    serial_port.write((message + '\r\n').encode())

def main(serial_port,baud_rate):
    # Open serial connections
    transmitter = radio_utils.RadioModule(serial_port, baud_rate)
    print("Transmitter radio parameters:")
    print(transmitter.get_current_parameters())
    print("Receiver radio parameters:")
    print(transmitter.get_current_parameters(remote=True))
    
    results = []

    try:
        for power in [1, 2, 5, 8, 11, 14, 17, 20]:
            if transmitter.set_transmit_power(power):
                radio_utils.time.sleep(1) # guard
                rssi_report_array = []
                for t in range(1,4): 
                    # Send message
                    send_message(transmitter, MESSAGE)
                    print(f"Sent: {MESSAGE}")
                    
                    # Get telemetry data from receiving radio
                    tdm_report, rssi_report = transmitter.get_output_data(remote=True)
                    if tdm_report and rssi_report is not None:
                        print(f"{tdm_report}\n{rssi_report}")
                        rssi_report_array.append(rssi_report)
                    else:
                        print("Failed to extract reports.")
                results_temp_dict = {'txPower' : power}
                results_temp_dict.update(average_reports(rssi_report_array))

                results.append(results_temp_dict)
    except KeyboardInterrupt:
        print("Stopping transmission.")

    radio_utils.write_results_to_csv(results,f'{FILEPATH}/results_power_var_obtained_remotely.csv')

if __name__ == "__main__":
    try: 
        serial_port = sys.argv[1]
        baud_rate = sys.argv[2]
    except IndexError:
        serial_port,baud_rate = radio_utils.pick_pickables()
    main(serial_port,baud_rate)