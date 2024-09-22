import csv
import zlib
import time
import os
import random
import string

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


# Forgive me for i have sinned
# packets_200B = generate_packets(payload_size=200, count=16)
# packets_64B = generate_packets(payload_size=64, count=16)
# packets_16B = generate_packets(payload_size=16, count=16)
DEFAULT_PACKET_LIST_200B = [b'A\x00\x01\x00\xbeYIKCJZBHCEHLVLGLWVDNFKCRKETITMDXINFCTBYEJTYWYFTTHPWEUWEHNMMFDNULKMRGQQZWQYTDGGFFUGZKETPFKSZFUGRTICQZVBGGHZBEWJEVWEQPGRSWKWVUCTYKLTSBZYDQIBUJDKEVSTUZMFQXDPJUSSFHSVZDYCWPWWIZFEQCLCCQKMKFPXCUPX\xe4\xab\xdegO',b'A\x00\x02\x00\xbeHLYQIMGCNJGSBITWNFMMEJNCGMRUKJDDPRHCYEMINNYYRKCQQIMVLCVECCWEWBNJCCIDBNUYTBKNTNXCQVIKUNCFNKMQQULHFFLPRVKRKLMJMPTYVCBTTLFUCBJBYPKZWWZDDUQQWZWMRBBYJYYRFHJYUZBNZULLPRZYJCTFBMRZFIJCZIUJTVIHRCTGXX\xc0\x7f\xbb\xfdO', b'A\x00\x03\x00\xbeQXQRBJZRTSHZGIZHUCSPFKNCSHSULCERLKWFFUSYJTJSCEFNEZUSZIBLXZLWQXGGIRBLPFHKCVCCVNHQLVGKEEUYRMVPFXWIYYVJIBMEJUEPSDLCZUNFMSGQFXDSVPSUUVKJFPRVLZITHUCMHGDKHPPWQVUSNLLPVHJBDMURXNFNTJWFMGKTQJJGXQPTXQ/\x93B\x1cO', b'A\x00\x04\x00\xbeIUIIHBITPBSYWWNKDYQDPMGSGKSTYBSQZCGXQZSJEEPKMBWBPLFQVSREEIZEPSFZKPEWDVYTFFGLZEVILFRSFEPTYGIIRNICIHQKFTBTKDEPJLDKDVQDXTENQBWFRKVNICDXRGPEBIFIXUCKZKBINUMXXHHSIHMWYYYNYKPZYGZCITRKWMYLHRZQXSPRJM\x1c:\x7f\xb0O', b'A\x00\x05\x00\xbeLXRTBTCXVRLQEQYCWDSSGULHBTHCTZUUUSLVIFNHJVFZYYVSJFKQMJQGKTSQSKQMYDKRYDCIUQRCCDNNZRFERPDPJNMMPECJJILLMGTCTVVRLLFURJZYSEGLTQTXXWTNDJIIRNQYREBJEUJKHYCXYGWDIPEFNCICCYGSZJDDLLTPPUKKBQPWTTRNPUBNMN\xb77\xb4\xcbO', b'A\x00\x06\x00\xbeGUQWMRQICUKYGRNMPGQLJRLNCKGKWWUQFMVLUPBCGEBXVFXMZHPNQNFVQFNRQPDGHSTKUNEDDCQBIKTXLURPZRUYLWJPNFFCJSPSVZVHIDBKXJCZBURIDJMHLQSCKUFQPQDFEQXRCZHQGFFTSGCIYQPLBNNBUUKMMGEYMUEMLVUTEDCSYTKGYTBDPGFTYG\x90\x86I\xd1O', b'A\x00\x07\x00\xbeISQLBWGNXLSVLXRDBCXKUPHQYRCXFNVPJURHZQZGZMQQPWQLDVTTSVSJILSNKGZVHGMFVQWYIZIZSJFPTNNUFIEFNCLMMNQDGXSMIDUGNFSDNGILULKFJZURSYYDINDYYJKZGPBWYPCYFVYSXMLDLVYYCNNQSBIJPQPIFRLQXMCSEJPJEVIZRPPHICGFDT\xa8\xa5\\\x06O', b'A\x00\x08\x00\xbeLFZHQVNZJHBPFVYYRQTHTIDULHYKEWKVJSUBHPXGSCMEXDHMDNUHWBIPULLFKCYGNQRCTRCEQQRJPKUIEFEREXCTTGSMHDISIIEUXDTTHYTZXRXEUIWSWNYBXQHLKCGIPUXSMVBFNUTPJKTLMQWPWJMNNYIECJNJDQKDYBMPYLLZEGYSXUSLSJGNBHXUDE\xd4w\x82lO', b'A\x00\t\x00\xbeZTZLHYKFWGBIFREEHKVHMEPBIBYRUXCEQFCZWJTTMPXQKPBUMHNUHZJCYXTZMWYDVGLPTDDCZBETLVJJNMEWCWUFMHJRJRJMQIWUUQSFJRKLBDDLIXTEWRVNLIQNYMUKINYGFSBBGEEJRMRLDIDWGWGLBTKSEURRDRBXEJZKNKJCYVUNJHPNXVLWHVDJZV&`\xc0\xb7O', b'A\x00\n\x00\xbeGZFWPZUZJRYTVXSGSRWECLSNMMBMBHJCJYBXJLSMSGMDIPXSRLVUEXYXEVVDRJQNRPWDHYKEFUPUBZHKYFNFBBTVEFUSGSITLFCILPSWHECLGVIBWIJGMGXFEZIWERHSQRBFYZXBRPVRKBLGGLBETXIUNYFWYCEXKWLWZTTHZMEELNWLTUDWWXTWFEMZJW\x1fj\x92\xf3O', b'A\x00\x0b\x00\xbeWQILTWBVQJBJXFZYDHPMSESTDQIMBGRMDTMVETZZKPZVVWMGMTWLVHGNKNHHKTFFJPWGYGQCYPZWQEZDPHEGEWQXERGKZFTNRWSCISKILWLBIKHHYBPHXKPJCSNNJVKYWIEIDECNHCXHDSQGNVLMKHMDTFCIUPTYPZISQQPKGKJJWSZRGCTVBRLBHNBBEMV\x81c\xceO', b'A\x00\x0c\x00\xbeEHDIZJIXBDDXCBVHQDLJMSJXYNTSGFDPRPIIXCIPYLNYTUVPKGXXRSRRGQIXXBIBECXUDDRHSIEFRYHUTBDKPWVBZNJFJWMVWSRHVDYCWGESFYJFRQCIUEKQPLKJQYQIXNJRJDTBEXWFLDYIHDBNYGCEGRYYHFVJBUQJESISLPBJZKHBENBMPGPBKPTCXF\xd9\tMGO', b'A\x00\r\x00\xbeYVVSBESZNXDVZRJEVMTCVBXTPLUGLWKQTBFEEMHZPKDXFQGCFLKTCYXPRUXTHLZQBINVDHJGWRTDRWHTSHDVKBNPVTVMCYNQHKEYWQSTRQYUTPIEGNTGTVRMXLCJYQLYRTTRLIWVBRIUZFUPQMWZCWWECTMWLHZDMLMBVBEPDKRXQYTSNQILSCEHZDPUTP\xc0\xd6\x0e\x7fO', b'A\x00\x0e\x00\xbeTIUWJBRXGXFVXZHWCYHEUJZGJJUMLUJRUVCYCCTHTFDCYXUGFRRPGWXWPZKGPJIUEHDVWSKYVVKMPWCTQMLBSTKDHNJBZNNCYBRYMMYGRLUWTNYWUKRTVZYUWGVWHFBWQUMMQZGTQFDUSYHRTZEJEVYUJPVSQYWDUWGUREDXKMBMWRGFWRCKUNWCCJXJKM\x08\xd6\x0c\xc2O', b'A\x00\x0f\x00\xbeJDEWKWXBTWVPWKJKTWMZSEFFHNDWPPLECYVYNIMGPBVYKQPQXFUQFGHIDHNXVHEYUPLYQWFBDCMKFGUMRNCYBZTGWDMNCEBLRUHGPFUQWITMTJYGWEGHRMDEKIYFUUQFKWWDTVWRDVZVBKCLFYRNVUVGKNYJNWUVGYVUFQGITHWUYQLQZRTUGIXFVINNXW\xf4B\x8dIO', b'A\x00\x10\x00\xbeQWSDUEBHYITNPPCEUXHQMFVDVXHPDQVZMKUSDSZBCQTCRXQPHCRHNFJSGCTNMXEYRDPTNVJHXGXNEIBTTXWULNSCPTSSILVXBZRNQVSQWJSIUFRRPQLPJMCJTIWSVWFGDRLWJCGPSBUXBCVSKVRFHBVIZEHTIGJRYJJZMGVZCFGBXSTMBQNSCUSFWBHIWG\xb6\x8fc"O']
DEFAULT_PACKET_LIST_64B = [b"A\x00\x01\x006BZGZFSJUQHWJPQLJEYRIUKTBEKYDTNTCEDLKVFKGUZLGPBGLUPRQCI\xa6'\x0b\xc5O", b'A\x00\x02\x006YVQGYURNVFNKZTXIPNLZICXRNFNRMGUCFSQPVRETVLBQHQXCCILGRF\x01\xdf\xd7\xcfO', b'A\x00\x03\x006GZWEDKWGXZQXUQZSJPNMVHDUWXCSGZJMJGLWTLCEHIBIFHXNIULCXEp\x7fJ\xb7O', b'A\x00\x04\x006NXJRFLGWKFWSQUKVTNQSDEWPRSPCRXCVQBEESTVQMFZMMXDHZBRBMQ\xc4w\x90\xceO', b'A\x00\x05\x006LCNCISEJQPVMZSYIPLXETJTWWNXGLRQGKUKSJWUBMMSUDSUMMWYJSC?\xecR\x7fO', b'A\x00\x06\x006ICFFYWYMJKIKVINUMZLNFGFYZDUJDZXYWUWUCIFFWQGRNUKNIZQGMRm\x89\xc5\xa4O', b'A\x00\x07\x006RWYLNQPHJNNESHCLWEZBCQNRDMQICSCSYNZGVTWXBWGFGDBFLISEVL\xadu\x144O', b'A\x00\x08\x006IPYQNJQYQTHMJHISYBNSZUTFWCRQYLXJGMSZRNMUSIMGDYLQUVUWJJ\x94\x0bc\xc2O', b'A\x00\t\x006YKIELRCIENBEURTZNBEYWPRINEFINDGXFYRPEUUBXFQXDNSIGKUWZK\x01X\xb8:O', b'A\x00\n\x006UWHFEYUUWIKKYVUXYIMXFEZPEVRHMYGZSCLPGZSPNTLVEUMECZUIWIsw\x82\xb2O', b'A\x00\x0b\x006WKKVNMUDEDCWYRTMMLWQCIPBQIDFHCRVPNDVXCLPWJRESPIQIWRZIQ\x0f\x95 \xbeO', b'A\x00\x0c\x006HDHEGGKFBDXXFSNQXSQBWYKBDJJBKVXYINNTEIIPHJKHGQFRCCWLLKs\xc8\xe5\xb9O', b'A\x00\r\x006GTGXTPCBGUXHHVEEESMQXKRWNISMJTIKRJWQYZQXSMITJGKYRBDUQU\xc6\x120\xe5O', b'A\x00\x0e\x006TPKXHJNZYHQFVHQMMZSUVYDVNRUDXJUCYENTUYCFNNVWRLERZBRLDX\xf4&\xe76O', b'A\x00\x0f\x006TWZZUXCPSIECZMITVDFYUHPCYHYRXCXCWPYPDGMQJLKSZKNXZWRFJG\x07\xc8v>O', b'A\x00\x10\x006MMRXBUIZWYYZKHLLRDQBGBZSJRYJNEBBMZQDJIDFKFYSRTGLYZHTMV\xf8\xfeveO']
DEFAULT_PACKET_LIST_16B = [b'A\x00\x01\x00\x06NCBXLR7;\xdf\xe5O', b'A\x00\x02\x00\x06FTEUDG\x00.\xef\xd6O', b'A\x00\x03\x00\x06VUMXHGH:$\x0eO', b'A\x00\x04\x00\x06YDJPJH\xb1\xc0S2O', b'A\x00\x05\x00\x06QPEDXY\x8e\x80\xbf\x85O', b'A\x00\x06\x00\x06IMCQYI\xfb\xd2O\xe7O', b'A\x00\x07\x00\x06STKPEM\x06xT6O', b'A\x00\x08\x00\x06GKLCXC8U\xbf\xb2O', b'A\x00\t\x00\x06REJSBSW\xd2\x90\xabO', b'A\x00\n\x00\x06MPLVGY\x8a\xdd\x84\xbeO', b'A\x00\x0b\x00\x06ESVUEF\xb4\x89\x0e\x95O', b'A\x00\x0c\x00\x06SXTQVN\xb0\x83\x1a<O', b'A\x00\r\x00\x06IIDRMK\xd36GcO', b'A\x00\x0e\x00\x06CSSHQZ1\xc8\xe3\xccO', b'A\x00\x0f\x00\x06NYHIZQ"aF\x1aO', b'A\x00\x10\x00\x06WEIZUZfG]aO']


def write_results_to_csv(results, filename):
    file_exists = os.path.exists(filename)
    keys = results[0].keys()
    
    with open(filename, 'a', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        
        if not file_exists:
            dict_writer.writeheader()  # Write headers only if the file does not exist
        
        dict_writer.writerows(results)  # Append the rows

def calculate_checksum(data: bytes) -> int:
    """Calculate CRC32 checksum for error detection."""
    return zlib.crc32(data)

def create_packet(sequence_number: int, total_size: int) -> bytes:
    """Create a packet of exact total size B with a header, payload, and CRC32 checksum."""
    start_marker = b'A'  # Start marker (1 byte)
    end_marker = b'O'    # End marker (1 byte)
    
    # The fixed size of the packet excluding the payload (start_marker, sequence_number, length, checksum, and end_marker)
    header_size = 1  # start_marker
    seq_len_size = 4  # sequence_number (2 bytes) + length (2 bytes)
    checksum_size = 4  # CRC32 checksum
    footer_size = 1  # end_marker
    fixed_size = header_size + seq_len_size + checksum_size + footer_size
    
    # Calculate the payload size based on the total_size (B) of the full packet
    payload_size = total_size - fixed_size
    
    # Generate random payload data (capital letters, excluding 'A' and 'O')
    allowed_characters = string.ascii_uppercase.replace('A', '').replace('O', '')
    payload_data = ''.join(random.choice(allowed_characters) for _ in range(payload_size)).encode('ascii')
    
    # Convert sequence number and payload size to 2-byte fields
    sequence_number_bytes = sequence_number.to_bytes(2, byteorder='big')
    length_bytes = payload_size.to_bytes(2, byteorder='big')
    
    # Construct the packet body without the markers
    packet_body = sequence_number_bytes + length_bytes + payload_data
    
    # Calculate CRC32 checksum for the packet body
    checksum = calculate_checksum(packet_body).to_bytes(4, byteorder='big')
    
    # Construct the full packet: start_marker + packet_body + checksum + end_marker
    full_packet = start_marker + packet_body + checksum + end_marker
    
    return full_packet

def generate_packets(total_size: int, count: int):
    """Generate `count` packets of a specific payload size."""
    packets = []
    for seq_num in range(1, count + 1):
        packet = create_packet(sequence_number=seq_num, total_size=total_size)
        packets.append(packet)
    return packets

# Decoding function to interpret packets
def decode_packet(packet: bytes):
    """Decode and validate a packet. Returns a tuple (sequence_number, payload) or raises an error."""
    # Ensure it starts and ends with the correct markers
    if packet[0:1] != b'A' or packet[-1:] != b'O':
        raise ValueError("Invalid packet markers")
    
    # Extract sequence number and payload length from the header
    sequence_number = int.from_bytes(packet[1:3], byteorder='big')
    length = int.from_bytes(packet[3:5], byteorder='big')
    
    # Extract payload data (minus start/end markers and checksum)
    payload_data = packet[5:5 + length]
    
    # Extract the checksum
    checksum = int.from_bytes(packet[5 + length:5 + length + 4], byteorder='big')
    
    # Verify the checksum
    packet_body = packet[1:5 + length]  # Exclude start/end markers and checksum
    if checksum != calculate_checksum(packet_body):
        raise ValueError("Invalid checksum")
    
    # Return the decoded data (sequence number and payload)
    return sequence_number, payload_data
    
def calculate_ber(bytes_sent: bytes, bytes_received: bytes) -> float:
    # Bit Error Rate calculation 
    if len(bytes_sent) != len(bytes_received):
        print((f"WARNING sequences are not of equal length. (sent={len(bytes_sent)} received={len(bytes_received)})"))
        # Pad the received sequence with zeros
        bytes_received = bytes_received.ljust(len(bytes_sent), b'\x00')
    

    # Count the number of bit errors
    bit_errors = 0
    total_bits = len(bytes_sent) * 8  # Total bits is length in bytes * 8

    for b1, b2 in zip(bytes_sent, bytes_received):
        # Count differing bits using XOR
        diff = b1 ^ b2
        bit_errors += bin(diff).count('1')  # Count the number of 1s in the binary representation

    # Calculate and return BER
    ber = bit_errors / total_bits
    return ber
    
def calculate_per(sent_packets_count,all_received_bytes) -> int:
    # Packet Error Rate calculation (PER)
    received_correct_packets_count = len(extract_packets(all_received_bytes))
    try:
        return (sent_packets_count-received_correct_packets_count)/sent_packets_count
    except ZeroDivisionError:
        return 0


def send_packets_at_defined_speed(transmitter,predefined_packets:list[bytes],number_of_packets_to_send:int,speed:int, log_file = None):
   # assumes that predefined_packets are all the same size
   print(f'sending {len(predefined_packets[0])}B packets at {speed} packets/s ')
   for i in range(number_of_packets_to_send):
        packet_index = i % len(predefined_packets)  # modulo to repeat packets -> this allows to have custom amount of packets e.g. 18
        packet = predefined_packets[packet_index]
        transmitter.write(packet)
        if log_file is not None:
            time_ms = int(time.time()*1000)
            log_file.write(f"{time_ms}: {packet}\n")
            log_file.flush()

        time.sleep(1/speed) # packets/s
        print(f"Sending packet {i + 1}: {(packet)}")

def str2bin(input_str: str) -> str:
    # converts normal string to bit representation string
    # Remove line breaks and spaces
    input_str = input_str.replace("\n", "").replace(" ", "")

    # Convert each character to its ASCII code and then to binary
    binary_representation = ''.join(f'{ord(char):08b}' for char in input_str)
    return binary_representation

def get_checksum_list(packet_list,checksum_size = 4):
    # CRC32 checksum is by default 4 Bytes long
    checksum_list = []
    for packet in packet_list:
            checksum_list.append(packet[-checksum_size-1:-1])
    return checksum_list


def extract_packets(data: bytes) -> list:
    """Extract valid packets from a concatenated byte string."""
    packets = []
    index = 0
    total_length = len(data)

    while index < total_length:
        # Look for the start marker 'A'
        if data[index:index + 1] != b'A':
            index += 1
            continue  # Move to the next byte if not found

        # Make sure there are enough bytes for reading the header (min 7 bytes)
        if total_length - index < 7:  # 1 (start) + 2 (seq) + 2 (len) + 1 (end)
            break

        # Read sequence number and payload length
        sequence_number = int.from_bytes(data[index + 1:index + 3], byteorder='big')
        payload_length = int.from_bytes(data[index + 3:index + 5], byteorder='big')

        # Calculate total packet size
        packet_size = 1 + 2 + 2 + payload_length + 4 + 1  # start + seq + len + payload + checksum + end

        # Check if the entire packet is available
        if total_length - index < packet_size:
            break  # Not enough bytes for a full packet

        # Extract payload data
        payload_data = data[index + 5:index + 5 + payload_length]

        # Check if the payload contains only capital letters
        if not all(b in string.ascii_uppercase.encode('ascii') for b in payload_data):
            index += 1
            continue  # Skip this packet if payload is invalid

        # Extract the checksum
        checksum = data[index + 5 + payload_length:index + 5 + payload_length + 4]

        # Validate the CRC32 checksum
        packet_body = data[index + 1:index + 5 + payload_length]  # Exclude start/end markers and checksum
        if calculate_checksum(packet_body) == int.from_bytes(checksum, byteorder='big'):
            # Include the end marker in the extracted packet
            packets.append(data[index:index + packet_size])  # Append the full packet to the list

        # Move the index forward to the next potential packet
        index += packet_size

    return packets
                
# packets_200B = generate_packets(total_size=200, count=16)
# packets_64B = generate_packets(total_size=64, count=16)
# packets_16B = generate_packets(total_size=16, count=16)
# print(f"DEFAULT_PACKET_LIST_16B = {packets_16B}")
# print(f"DEFAULT_PACKET_LIST_64B = {packets_64B}")
# print(f"DEFAULT_PACKET_LIST_200B = {packets_200B}")


# print(decode_packet(packets_64B[0]))
