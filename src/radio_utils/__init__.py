import serial  # pip install pyserial
import time
import serial.tools.list_ports
import re

serial.Serial.flush
def detect_baud_rate(port):
    """
    Detects the baud rate of the connected SiK radio.

    Args:
        port (str): The serial port to check.

    Returns:
        int: The detected baud rate, or None if detection failed.
    """
    baud_rates = [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200]
    for baud in baud_rates:
        print("Checking: " + str(baud))
        try:
            with serial.Serial(port, baud, timeout=1) as ser:
                # Clear the buffer
                ser.reset_input_buffer()
                ser.reset_output_buffer()
                # Enter AT command mode
                time.sleep(1)
                ser.write(b'+++')
                time.sleep(1)
                ser.write(b'ATI\r\n')
                time.sleep(1)
                response = ser.read_all().decode(errors='ignore').strip()
                if 'SiK' in response:
                    ser.write(b'ATO') # leave command mode
                    return baud
        except serial.SerialException:
            pass
    return None

def list_serial_ports():
    """
    Lists available serial port names.

    Returns:
        list: List of available serial port names.
    """
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def pick_pickables():
    """
    Prompts the user to select a serial port and enter or detect a baud rate.

    Returns:
        tuple: Selected serial port and baud rate, or None if the selection failed.
    """
    ports = list_serial_ports()
    if not ports:
        print("No serial ports found.")
        return

    print("Available serial ports:")
    for i, port in enumerate(ports):
        print(f"{i}: {port}")

    # Prompt user to select a serial port
    port_index = int(input("Select the serial port index: "))
    if port_index < 0 or port_index >= len(ports):
        print("Invalid index.")
        return

    selected_port = ports[port_index]

    # Prompt user for baud rate or attempt to detect automatically
    detected_baud = input("Insert baud rate (press enter if not sure): ").strip()
    if detected_baud == '':
        detected_baud = detect_baud_rate(selected_port)
        if detected_baud:
            print(f"Successfully detected baud rate: {detected_baud}")
        else:
            print("Failed to detect baud rate.")
            return
    else:
        detected_baud = int(detected_baud)

    return selected_port, detected_baud

def display_parameters_descriptions():
    description = """
    S0:FORMAT=<value>
    Command: ATS0?
    Description: The data format used by the radio.

    S1:SERIAL_SPEED=<value>
    Command: ATS1?
    Description: The baud rate for communication between the radio and the connected device (57 = 57600bps).

    S2:AIR_SPEED=<value>
    Command: ATS2?
    Description: The data transmission rate over the air between radios (between 1 and 256 kbs)

    S3:NETID=<value>
    Command: ATS3?
    Description: Identifies the network, allowing multiple sets of radios to operate independently in the same area (e.g., 0-255).

    S4:TXPOWER=<value>
    Command: ATS4?
    Description: The transmit power level of the radio in dBm.

    S5:ECC=<value>
    Command: ATS5?
    Description: Enables or disables Error Correction Coding (ECC) to improve data reliability (0 for off, 1 for on).

    S6:MAVLINK=<value>
    Command: ATS6?
    Description: Optimizes the radio for MAVLink data transmission (0=no MAVLink framing, 1=frame mavlink, 2=low latency mavlink).

    S7:OPPRESEND=<value>
    Command: ATS7?
    Description: OppResend parameter, related to packet retransmission.

    S8:MIN_FREQ=<value>
    Command: ATS8?
    Description: Sets the minimum operating frequency of the radio.

    S9:MAX_FREQ=<value>
    Command: ATS9?
    Description: Sets the maximum operating frequency of the radio.

    S10:NUM_CHANNELS=<value>
    Command: ATS10?
    Description: The number of frequency channels used by the radio.

    S11:DUTY_CYCLE=<value>
    Command: ATS11?
    Description: Limits the percentage of time the radio spends transmitting (0-100).

    S12:LBT_RSSI=<value>
    Command: ATS12?
    Description: Listen Before Talk (LBT) Received Signal Strength Indicator (RSSI) threshold.

    S13:MANCHESTER=<value>
    Command: ATS13?
    Description: Enables or disables Manchester encoding to reduce errors (0 for off, 1 for on).

    S14:RTSCTS=<value>
    Command: ATS14?
    Description: Enables or disables RTS/CTS hardware flow control (0 for off, 1 for on).

    S15:MAX_WINDOW=<value>
    Command: ATS15?
    Description: Sets the maximum window size for packet transmission.
    """
    print(description)

def display_ATI_commands():
    ATI_commands = """
    The AT commands available are:
    +++ - enter command mode
    ATI - show radio version
    ATI2 - show board type
    ATI3 - show board frequency
    ATI4 - show board version
    ATI5 - show all user settable EEPROM parameters
    ATI6 - display TDM timing report
    ATI7 - display RSSI signal report
    ATO - exit AT command mode
    ATSn? - display radio parameter number 'n'
    ATSn=X - set radio parameter number 'n' to 'X'
    ATZ - reboot the radio
    AT&W - write current parameters to EEPROM
    AT&F - reset all parameters to factory default
    AT&T=RSSI - enable RSSI debug reporting
    AT&T=TDM - enable TDM debug reporting
    AT&T - disable debug reporting"""
    print(ATI_commands)

    ## Parsing Methods ##
def parse_ati5_response(response):
    """
    Parse the response from the ATI5 command into a dictionary.
    Args:
        response (str): The ATI5 command response string.
    Returns:
        dict: A dictionary with parameter names as keys and their corresponding values.
    """
    # Remove leading and trailing whitespace and split the response into lines
    lines = response.strip().split('\r\n')
    # Initialize an empty dictionary to hold the parameters
    parameters = {}
    # Iterate over each line and split by '=' to form key-value pairs
    for line in lines:
        if line.startswith('S'):
            key, value = line.split('=')
            parameters[key] = int(value)
    return parameters

def parse_ati6_response(response):
    """
    Parses the response from the ATI6 command to extract TDM timing report details.
    Args:
        response (str): The response string from the ATI6 command.
    Returns:
        dict: A dictionary containing the parsed values.
    """
    result = {
        'silence_period': None, # indicates the time interval when no data transmission occurs.
        'tx_window_width': None,
        'max_data_packet_length': None 
    }
    
    match = re.search(r'silence_period: (\d+)', response)
    if match:
        result['silence_period'] = int(match.group(1))
    match = re.search(r'tx_window_width: (\d+)', response)
    if match:
        result['tx_window_width'] = int(match.group(1))
    match = re.search(r'max_data_packet_length: (\d+)', response)
    if match:
        result['max_data_packet_length'] = int(match.group(1))
    return result

def parse_ati7_response(response):
    """
    Parses the response from the ATI7 command to extract RSSI and other diagnostics.
    Args:
        response (str): The response string from the ATI7 command.
    Returns:
        dict: A dictionary containing the parsed values.
    """
    result = {
        'L_RSSI': None, # local
        'R_RSSI': None, # remote
        'L_noise': None,
        'R_noise': None,
        'packets': None, # number of packets processed
        'tx_errors': None, # transmit errors
        'rx_errors': None, #  receive errors
        'successful_tx': None,
        'successful_rx': None,
        'ecc_corrected': None,
        'ecc_uncorrected': None,
        'temperature': None,
        'dco': None # number of DC offset corrections
    }
    
    match = re.search(r'L/R RSSI: (\d+)/(\d+)', response)
    if match:
        result['L_RSSI'] = int(match.group(1))
        result['R_RSSI'] = int(match.group(2))
    match = re.search(r'L/R noise: (\d+)/(\d+)', response)
    if match:
        result['L_noise'] = int(match.group(1))
        result['R_noise'] = int(match.group(2))
    match = re.search(r'pkts: (\d+)', response)
    if match:
        result['packets'] = int(match.group(1))
    match = re.search(r'txe=(\d+)', response)
    if match:
        result['tx_errors'] = int(match.group(1))
    match = re.search(r'rxe=(\d+)', response)
    if match:
        result['rx_errors'] = int(match.group(1))
    match = re.search(r'stx=(\d+)', response)
    if match:
        result['successful_tx'] = int(match.group(1))
    match = re.search(r'srx=(\d+)', response)
    if match:
        result['successful_rx'] = int(match.group(1))
    match = re.search(r'ecc=(\d+)/(\d+)', response)
    if match:
        result['ecc_corrected'] = int(match.group(1))
        result['ecc_uncorrected'] = int(match.group(2))
    match = re.search(r'temp=(-?\d+)', response)
    if match:
        result['temperature'] = int(match.group(1))
    match = re.search(r'dco=(\d+)', response)
    if match:
        result['dco'] = int(match.group(1))
    return result

def compare_params(params1, params2):
    """
    Compares two parameters dicts and returns dict with parameters names as keys and booleans as its values (outputs True in dict if params1 and params2 have a mismatch in key name; if there's at least one mismatch returns dict)
    Returns False value if both parameters lists are the same
    """
    output_dict = {}
    false_count = 0
    # Check for keys in params1
    for key in params1:
        if key in params2:
            if params1[key] == params2[key]:
                output_dict[key] = True
            else:
                output_dict[key] = False
                false_count += 1
        else:
            output_dict[key] = True

    # Check for keys in params2 not present in params1 (i.e. leave that val as it is)
    for key in params2:
        if key not in params1:
            output_dict[key] = True
    print(f'{false_count} parameters mistmatch(es) found from requested values')
    if false_count == 0:
        return False
    return output_dict


class RadioModule(serial.Serial):
    def __init__(self, serial_port, baud_rate, timeout=1):
        super().__init__(port=serial_port, baudrate=baud_rate, timeout=timeout)
        # useful parent funcs
        # .read_all()
        # .write()
    def __del__(self) -> None:
        # self.leave_command_mode() # might be the reason for inconsistent behaviour (?)
        return super().__del__()

    ## setters ##
    def send_at_command(self, command):
        pattern = re.compile(r'^(\+\+\+|ATI(2|3|4|5|6|7)?|RTI(2|3|4|5|6|7)?)$|^ATO$|^(ATS\d+(\?|(=\d+))|RTS\d+(\?|(=\d+)))$|^(ATZ|RTZ)$|^(AT&W|RT&W)$|^(AT&F|RT&F)$|^(AT&T(=RSSI|=TDM)?|RT&T(=RSSI|=TDM)?)$')
        if not pattern.match(command):
            print('Invalid AT command: ' + command)
            display_ATI_commands()
            return ''
        self.write(command.encode() + b'\r\n')
        print(f'sending {command} command to the radio')
        time.sleep(2)
        response = self.read_all().decode(errors='ignore').strip()
        setter_pattern = re.compile(r'^(ATS\d+=\d+|RTS\d+=\d+)$')
        if setter_pattern.match(command):
            print(f'Setter command executed: {command}, Response: {response}')

        
        return response

    def enter_command_mode(self, verbose = False):
        if ('SiK' in self.send_at_command('ATI')):
            time.sleep(1)
            if verbose:
                print("Already in command mode")
            return True
        for _ in range(3):  # Try multiple times
            self.reset_input_buffer()
            self.reset_output_buffer()
            time.sleep(1)
            self.write(b'+++')
            time.sleep(1)
            if 'SiK' in self.send_at_command('ATI'):
                return True
        return False

    def leave_command_mode(self):
        self.send_at_command('ATO')

    def set_transmit_power(self, power, remote = False):
        valid_powers = [1, 2, 5, 8, 11, 14, 17, 20] # max 20dbm, if not one of these it will be set implicitly anyway to the higher one
        if power not in valid_powers:
            print(f"Invalid power level: {power}. Valid levels: {valid_powers}")
            return
        if self.enter_command_mode():
            if remote:
                response = self.send_at_command(f'RTS4={power}')
            else:
                response = self.send_at_command(f'ATS4={power}')
            if 'OK' in response:
                if 'OK' in self.send_at_command('AT&W'):
                    print(f'Successfully set transmit power to {power} dBm and saved to EEPROM.')
                    return True
                else:
                    print('Failed to save to EEPROM.')
            else:
                print('Failed to set transmit power.')
        else:
            print("Failed to enter command mode")
        return False
    
    def set_air_rate(self, air_rate):
        valid_air_rates = [2, 4, 8, 16, 19, 24, 32, 48, 64, 96, 128, 192, 250] # if not one of these it will be set implicitly anyway to the higher one
        if air_rate not in valid_air_rates:
            print(f"Invalid air rate: {air_rate}. Valid levels: {valid_air_rates}")
            return
        if self.enter_command_mode():
            response = self.send_at_command(f'RTS2={air_rate}')
            time.sleep(0.5)
            if 'OK' not in response:
                print("failed to set air rate in the receiver") # sometimes it sets anyway - might not get OK in time - perhaps check parameters instead? retry if not set
            response = self.send_at_command(f'ATS2={air_rate}')
            if 'OK' in response:
                if 'OK' in self.send_at_command('AT&W'):
                    print(f'Successfully set air rate to {air_rate} kbs and saved to EEPROM.')
                    return True
                else:
                    print('Failed to save to EEPROM.')
            else:
                print('Failed to set transmit power.')
        else:
            print("Failed to enter command mode")
        return False
    def set_mav_link(self, mav_link_option, remote = False):
        valid_mav_link_options = [0, 1, 2]
        if mav_link_option not in valid_mav_link_options:
            print(f"Invalid mav link option: {mav_link_option}. Valid options: {valid_mav_link_options}")
            return
        if self.enter_command_mode():
            if remote:
                response = self.send_at_command(f'RTS6={mav_link_option}')
            else:
                response = self.send_at_command(f'ATS6={mav_link_option}')
            if 'OK' in response:
                if 'OK' in self.send_at_command('AT&W'):
                    print(f'Successfully set mav link option to {mav_link_option} and saved to EEPROM.')
                    return True
                else:
                    print('Failed to save to EEPROM.')
            else:
                print('Failed to set transmit power.')
        else:
            print("Failed to enter command mode")
        return False
    def set_eec(self, eec_op, remote = False):
        valid_eec_op = [0, 1]
        if eec_op not in valid_eec_op:
            print(f"Invalid eec option: {eec_op}. Valid options: {valid_eec_op}")
            return
        if self.enter_command_mode():
            if remote:
                response = self.send_at_command(f'RTS5={eec_op}')
            else:
                response = self.send_at_command(f'ATS5={eec_op}')
            if 'OK' in response:
                if 'OK' in self.send_at_command('AT&W'):
                    print(f'Successfully set EEC option to {eec_op} and saved to EEPROM.')
                    return True
                else:
                    print('Failed to save to EEPROM.')
            else:
                print('Failed to set transmit power.')
        else:
            print("Failed to enter command mode")
        return False

    def set_params_to_request(self,requested_params) -> None:
        current_params = self.get_current_parameters()
        request_params_mismatch_dict = compare_params(current_params,requested_params)
        if request_params_mismatch_dict:
            for key, value in request_params_mismatch_dict.items():
                if not value:
                    s_parameter_num = key.split(':')[0]
                    value_to_set = eval(f'requested_params[\'{key}\']')
                    self.send_at_command(f'AT{s_parameter_num}={value_to_set}')
        else:
            print('Already set to requested values')

    ## getters ##
    def get_current_parameters(self,remote=False):
        if self.enter_command_mode():
            if remote:
                response = self.send_at_command('RTI5')
            else:
                response = self.send_at_command('ATI5')
            return parse_ati5_response(response)
        else:
            print("Failed to enter command mode")
    
    def get_output_data(self,remote=False,get_timing_report=False):
        """
        Extracts either a tdm and rssi reports as tuple of dicts or just rssi report dict

        Args:
            response (str): The response string from the ATI6 command.
        """
        if self.enter_command_mode():
            if remote:
                if get_timing_report:
                    tdm_report = parse_ati6_response(self.send_at_command('RTI6'))
                rssi_report = parse_ati7_response(self.send_at_command('RTI7'))
            else:
                if get_timing_report:
                    tdm_report = parse_ati6_response(self.send_at_command('ATI6'))
                rssi_report = parse_ati7_response(self.send_at_command('ATI7'))
            if get_timing_report:
                return tdm_report, rssi_report
            else: 
                return rssi_report
        else:
            print("Failed to enter command mode")
            return

# if __name__ == '__main__':
#     # selected_port, detected_baud = pick_pickables()
#     selected_port ='COM5'
#     detected_baud = 57600
#     if selected_port and detected_baud:
#         radio = RadioModule(selected_port, detected_baud)
#         current_parameters = radio.get_current_parameters()
#         print(current_parameters)
#         # Change power as needed
#         radio.set_transmit_power(20)  # Example power level to set
#         tdm_report, rssi_report = radio.get_output_data()
#         print(rssi_report)
#         print(tdm_report)
#         radio.leave_command_mode()