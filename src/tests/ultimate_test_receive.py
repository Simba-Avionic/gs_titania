import sys
import os
# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import radio_utils
from radio_utils.calculations import average_reports
import radio_utils.testing as t
import re

# Consts
DEFAULT_PARAMS = radio_utils.testing.DEFAULT_PARAMS
# DEFAULT_PARAMS['S2:AIR_SPEED'] = 2
# DEFAULT_PARAMS['S4:TXPOWER'] = 20
# DEFAULT_PARAMS['S10:NUM_CHANNELS'] = 10
DEFAULT_PACKET_LIST_200B = radio_utils.testing.DEFAULT_PACKET_LIST_200B
DEFAULT_PACKET_LIST_64B = radio_utils.testing.DEFAULT_PACKET_LIST_64B
DEFAULT_PACKET_LIST_16B = radio_utils.testing.DEFAULT_PACKET_LIST_16B
FILEPATH = os.path.dirname(__file__)

def parse_sent_inputs(current_inputs):
    try:
        current_inputs = re.search(r'a(.*?)o', current_inputs).group(1)
        current_inputs = [pair.strip() for pair in current_inputs.split(';') if pair]
        if current_inputs[2][-1:] == 'BB': # idk, happened once
            current_inputs[2] = current_inputs[:-1]
        # Create a dictionary from the current_inputs
        result_dict = {}
        for pair in current_inputs:
            key, value = pair.split('=')
            result_dict[key.strip()] = value.strip()
        return result_dict
    except AttributeError:
        return None
    

# def create_repeated_bit_sequence(num_of_packages, size_of_package): 
#     all_packages_concatenated = ''
#     current_packet_set_used = eval(f'DEFAULT_PACKET_LIST_{size_of_package}')
#     for i in range(num_of_packages):
#         all_packages_concatenated += current_packet_set_used[i%len(current_packet_set_used)].decode()
#     all_packages_concatenated = radio_utils.testing.str2bin(all_packages_concatenated)
#     return all_packages_concatenated

def create_repeated_byte_sequence(num_of_packages, size_of_package) -> bytes: 
    all_packages_concatenated = b''
    current_packet_set_used = eval(f'DEFAULT_PACKET_LIST_{size_of_package}')
    for i in range(num_of_packages):
        all_packages_concatenated += current_packet_set_used[i%len(current_packet_set_used)]
    return all_packages_concatenated

def create_csv_row(output_dict,current_inputs,all_received_bytes:bytes):
    result = []
    # received_bits = t.str2bin(all_received_bytes)
    input_dict = parse_sent_inputs(current_inputs)
    ber, per, bytes_lost, bytes_sent = ber_per_helper(input_dict,current_inputs,all_received_bytes)
    output_dict.update({'BER':ber, 'PER':per, 'BYTES_LOST%':bytes_lost/bytes_sent*100})
    input_dict.update(output_dict)
    result.append(input_dict)
    t.write_results_to_csv(result,f'{FILEPATH}/results/ultimate_results_received.csv')

def ber_per_helper(input_dict,current_inputs,all_received_bytes):
    input_dict = parse_sent_inputs(current_inputs)
    if type(input_dict) == None:
        print("KURDE BALANS ZA MOMENT WYPIERNICZY")
    else:
        sent_bytes = create_repeated_byte_sequence(int(input_dict['PACKET_AMOUNT']), input_dict['PACKET_SIZE'])
        sent_packets_count = int(input_dict['PACKET_AMOUNT'])  
        
    # incorrect_bytes_amount = t.check_incorrect_bytes(sent_bytes, all_received_bytes)
    ber,bytes_lost = t.calculate_ber(sent_bytes, all_received_bytes)
    per = t.calculate_per(int(sent_packets_count),all_received_bytes)
    return ber, per, bytes_lost, len(sent_bytes)

def save_bytes_chunk(data: bytes, log_file):
    """
    Saves a 16-byte chunk of data with a timestamp to a log file.
    """
    # Get the current timestamp
    timestamp = radio_utils.time.time()*1000
    
    # Format the log entry with the timestamp and data in hex
    log_entry = f"{timestamp} {data.hex()}\n"
    
    # Save to file
    log_file.write(log_entry)
    log_file.flush()  # Ensure the data is written immediately to the file
    # print(f"Chunk saved: {log_entry}")


def main():
    # Init
    # serial_port, baud_rate = radio_utils.pick_pickables()
    serial_port = 'COM7'
    baud_rate = 115200
    with radio_utils.RadioModule(serial_port, baud_rate, timeout=0.0001) as receiver: # idk why but that's the only way for read to work that i found
        receiver.reset_input_buffer()      
        receiver.reset_output_buffer()
        receiver.read_all()
        receiver.set_params_to_request(DEFAULT_PARAMS) # can comment it out to save some time if already set ---> best/easiest way to edit params
        receiver.leave_command_mode()
        # print(receiver.get_current_parameters()) # can comment it out to save some time
        # print(receiver.get_current_parameters(remote=True)) # can comment it out to save some time

        # Testing Stuff
        all_received_bytes = b''        
        log_chunk = b''
        log_file = open(f'{FILEPATH}/results/received_bytes_log.txt','a')
        while True:
            current_inputs = ''
            current_byte = receiver.read()
            if not (current_byte == b'' or current_byte == b'+'):
                print(current_byte)
                all_received_bytes += current_byte
                log_chunk += current_byte
                if len(log_chunk) == 16:
                    save_bytes_chunk(log_chunk,log_file)
                    log_chunk = b''
                if current_byte == b'#':
                    all_received_bytes = all_received_bytes.replace(b'#',b'')
                    save_bytes_chunk(log_chunk,log_file)
                    log_chunk = b''
                    # all_received_bytes = all_received_bytes.replace('ATI\r\n','') # might leak in?
                    while True:
                        receiver.write('@@@'.encode())
                        radio_utils.time.sleep(1.5)
                        current_inputs += receiver.read(150).decode()
                        radio_utils.time.sleep(1.5)
                        current_inputs += receiver.read(150).decode()
                        if 'PACKET_SIZE' in current_inputs:
                            print(current_inputs)
                            output_dict = receiver.get_output_data()
                            print(output_dict)
                            create_csv_row(output_dict,current_inputs,all_received_bytes)
                            # with open('bytes_received.txt', 'a', newline='') as output_file:
                            #     output_file.write(f"{all_received_bytes}\n")
                            #     output_file.flush()
                            all_received_bytes = b''
                            receiver.flushInput()
                            receiver.flushOutput()
                            radio_utils.time.sleep(0.4)
                            for i in range(5):
                                receiver.write('$$$$$$$$$$$$$$$$$$'.encode())
                                radio_utils.time.sleep(0.4)
                            break    
                    
                    receiver.flushInput()
                    receiver.flushOutput()
                    current_byte = ''
        log_file.close()

if __name__ == "__main__":
    main()

