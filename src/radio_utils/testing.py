import csv
import os
import time

DEFAULT_PARAMS = {
    'S1:SERIAL_SPEED': 57,      # 57600 baudrate
    'S3:NETID': 18,
    'S5:ECC': 0,
    'S8:MIN_FREQ': 434550,
    'S9:MAX_FREQ': 434650,
    'S10:NUM_CHANNELS': 10,
    'S11:DUTY_CYCLE': 100,
    'S12:LBT_RSSI': 0,
    'S13:MANCHESTER': 0,
    'S14:RTSCTS': 0,
    'S15:MAX_WINDOW': 100
}

def write_results_to_csv(results,filename):
    keys = results[0].keys()
    with open(filename, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(results)

def generate_random_frame(size) -> bytes:
    return os.urandom(size)

def calculate_ber(sent_bits, received_bits) -> int:
    # Bit Error Rate calculation (BER)
    errors = sum(1 for s, r in zip(sent_bits, received_bits) if s != r)
    return errors / len(sent_bits)

def calculate_per(sent_packets, received_packets) -> int:
    # Packet Error Rate calculation (PER)
    errors = sent_packets - received_packets
    return errors / sent_packets

def send_frames_at_defined_speed(transmitter,predefined_frames,number_of_frames_to_send,speed):
   # assumes that predefined_frames are all the same size
   print(f'sending {len(predefined_frames[0])}B frames at {speed} frames/s ')
   for i in range(number_of_frames_to_send):
        frame_index = i % len(predefined_frames)  # modulo to repeat frames -> this allows to have custom amount of frames e.g. 18
        frame = predefined_frames[frame_index]
        transmitter.write(frame)
        time.sleep(1/speed) # frames/s
        print(f"Sending frame {i + 1}: {frame}")