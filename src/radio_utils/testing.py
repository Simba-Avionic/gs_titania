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
DEFAULT_PACKET_LIST_200B = [b'A\x00\x01\x00\xc8TJJEECFPLRUIEMSPNUMMIHCHWRFVVFPTYQSGQQVGUPJXVJHZZHTHNYEHLJEBRIHZVESLFIZMFJQMFQZCVXCRCYTYFQVZYGBKHPTNJPPYTJJRIDMLVGKYCPTUDXMYPQBNUVHXJNGYYVCFCPUYSRSERBRUPJNYIREFPHPNERBFYCKWJPGTEBSBYHPUIMQBCWCHYMCYSSZU\x08\xe8:\xaeO', b'A\x00\x02\x00\xc8LXEXFSRRSXRDXDHFRDBDDUSIEPHSJVWNDUQEQKEEMSZZPWSYXDBRGZSVLLIUDSVNPYVZCMVRFIHUIJDIZLCZPNBIHCNIIGCESFEXJELKQWHRNKBEFSBCCFEBEZIVYIPRGBKRLHHYFDREJSHYZLNXYTBEYXUBKWCKRQXUEUHKMGPGKBBHVXWFBFGJCGWJPYDDMMIMIMPQ@\xc5\xc0UO', b'A\x00\x03\x00\xc8WRRDRVQWQTQXYEKGCKDNXVKUUDBXDZLIKWZQMSLZTDEXTJFGTGZCWJBZYQFVPGGDEKVSTUBYWZNXZSSCQWRVUWJPLSWUMHJIVVVKGPSFKZGSICDXHCFBXVKXLIPBGZLFNWWZCWLGPLCKBWDDTXBEVMEDKWPDEHYJWCVLZKDJEBJUKNFBXJTMZZUZBBYDVSQMRFDHNTMZ\xec\x94\xe9\xd5O', b'A\x00\x04\x00\xc8DXHNSJZJCLXQGLJSZWRMWGFJKJYUEIJUGYZTJWDYBQRLLQENHZXLQKPLLZRBLHYGVPZBNURNZHESDJIJEUPUNLFICVVULLWXUEIMSVZKLNXRQEQBXCEFJHUXMSZRZSZEZMBHHNCMLVRFHRDRRRQEVBKNYUJLULPFZZLSGVBUJKKPMSVJVEMECJNMHCUXJVLVBJGRNQDZ\x98\x86\x05\xdaO', b'A\x00\x05\x00\xc8FUGHZDKQMIMINGHFYRIBNGQPYFWWTNZJZUTHZDRXUNHCCBTSZDESPEPBVTLLGXBSESXKXZMUBWQLCIBLZUUMUVSMWXIGVPQNWJCCTSKZYUQLDDEQHBUPHDKQKNYYRWDVCFVSTBFQTHQXXXPGDPENKVWULXCSEFFSWWZFFUWUUVVNJFPVHTLIDNHICDVTVVTTCNSKHNRB\x11\xecH]O', b'A\x00\x06\x00\xc8MYPWQZQQYEDLCLLLJLZHBUIYLGRHEDPEYZIXBQHMPLITMERULFQFEFYFTXSQJWKWWVYKUVJJGHNQNWFLGTHJZENIMCTCYKEWTZPLSHRZDWYQDKNJYBCESXXHLYNQQZFCYVKETYWTLXJGYIGBKDRIUSTJWLNMKDDWIIJHBNRBDVJTTENJFSPRZVCVCUBBIUJEKCPNSQCR\x92\x84\xb7\xeaO', b'A\x00\x07\x00\xc8NCTGRKRSMKHNHREPNHTMNGDPIJIIDWQYYSYWPPEQUFRHNHIZRFRDWSZJLIKCXRMHGPGIHMBGDLNZFEBIGVGSTGDNBSMCEZGWFQLFIPQFSYZLFNBFJYNKDNMCWRGWMJZFKQNJZQIPDKJBJTWEFTVFCJFEBFBDPTYPTZXXVINGVBVEENQILVSUXMEGDEDFEDLIQEFJHDFVk,\xe3{O', b'A\x00\x08\x00\xc8UWGLTVJIHGUYPVTQZZRZVZIFDZVNQKTFEUILSPGUJYXYPTMDPMPSMTSIPYMLHUVPRNKYJYRMPQYLXPNLBUZXXKIQVNDIXWPTFKBUSDVQEKCXRXHJCYYNYQNDSJTSXPKJRZGXEWPYMKZRUYRQHCDDITLRLFYTLLMPQTGPVUKHPPLGBYKPKIVDNTYICWCBPPZZSYISPVRN\xbe5\xcc\xbcO', b'A\x00\t\x00\xc8KBVDIBULYTILLRWFURSUKMDVWEWZNBPNYYHEMWPJHLCKMCIHBNREYBZSKBXKPLXUBWUMJXMNCVIQVRUSDILFCFNURNYNLURZBUNHDXEMFQCPRUBXCLDVBUZGXWSEBBMSNKQMWHTBSMZWEVGBMDYCJQINZGIHICIINSQPVRYWHKYFEIHVXVVLFFVGNDDLVCPJRZYISNCM\xd0\x15\xd3\\O', b'A\x00\n\x00\xc8RSJLEMMNCLSUFDVYGXTCFGMBETTKMGNISKIBDJTYLJGIIQRZZKELHEFDRZEYZPZFGCFCXWUMEJFDVYYBXRGCWQTTQNDKKCNGXZEPFGFZMPEDMTEWJVZGIGWMXECPGFDWFUUMKMYNHMXXIBUKGFEKGSNWTWLVFWQSKJEKPHJVPIKETXBNYUMGBHWTWDKFYTLCDJGRQEJU\xa2\xe8=\xdeO', b'A\x00\x0b\x00\xc8FGIFHEMMZDYCKBEGKTEMYJILTIUDKCBMPPSVZSVQKQGMHZRMVXZPIPEPFYLTHBVIJWCQVBYCSUXJRFLKFPQQQNLUEBWUZYGQJCMFGNQRIWWIJFTUEFRHWXNNIRKTPZXWKZPLXKYVUPTBMVUIXRCQUYDEFPQHQYVMWJGXTQZNYCVVXUWWWJRUKZWPKWSQEYQMPTSMHUCM\xbeO\xf9DO', b'A\x00\x0c\x00\xc8SIHWZPJBHKGDPQZVNMNNPEQXDCYTYRXTQEPULFRGJDDIMYXZXUKECRBGUMXNRMXCMEFGZTNEUXNCIGUUTJUKBNFHEEZGKZKIHTKSIFTYGMJCUYKVLCEKSUUDLBLFEDPKGGEJMVZJSHVFITVQFXEBKBSLGBJDXPJBEZTBJPBRDZHEMUTTWWDLUEUJXEKQUNJFRLUKRULL"\x8eo\xfbO', b'A\x00\r\x00\xc8MUFVQJQSEFKQSFGBPFQEFUSNQWYEVJBKULUREYNHCVRFXXRJQJWYMTTTVMLVKKXPMEPQNTRDBJTPTNUXZGPZSBWLXUZHZXLTJHFRKBKZLUYYWSGIDLHJQSJDVSPKJICNFJQMCLNSWUIRTZPHRCBCRINUPRZYWVBBSHXBPRHLXXEEKBNNWFHFUYQVSUFCYDVJXTWDRHIZ\xc6t\t\xf8O', b'A\x00\x0e\x00\xc8NIIUWVEDNDHTRYQMLCNVXGFXCEBQZQKCEWVNFQLLNBXTVRUVNBSHQZNJDXDXQFLFNWRMHZUHXENYSSQTGNVZYUBEDYMYPDSWPQZLBZHQBTWYJEFCUTZDXJHXZJEWRXTLMFDPQNBVGSZPFDZDYZBQVUDPHDVWBTLIWVVWZWXUWCYPWNKPULWDDHPRNVFRJUHRFKICYCQJ\x9b\xb7\xceIO', b'A\x00\x0f\x00\xc8FMCMCKLJGULWDEIXBLMIHWLUCFNEKNVKGEJYTDRCCPPNVUENTLGVTQBNLVCFJYVZQIIVYQFJEPDIYDJRCNNUTSDTFZMBDXRQNIHFGVRCYVXFQDMTWJHEYMEMPFBLTVYXTUTGHNMQGRPGMDJZIISZWTKFGPTDHRRZJJSRVBQVPSTVXSNMUTKGKMBEZNDLPKNDEELRKPNM\x91\xe9\xecKO', b'A\x00\x10\x00\xc8XDDSEMWMWYHICEFENBESKINBSGQPFBPXTFLDXURCYWULSUQFSZSZLRMPJRZVRHGGPUKMHHSPFGIGYZDTPLWQMXXYHFILFEPIVNWDMYXVLJTXQWWWNIUFMJRXXHMUXHYSJLILMDRKWEKNTTRMQPVUUMNTEEETBVBPQZXFJSELXSJTUBJDMYJGQEFGDQSMUMPMHGMQSFQT\xa2\xd96wO']
DEFAULT_PACKET_LIST_64B = [b'A\x00\x01\x00@NKYVTHWLJGKKQSWRHETJRSBTGHTXUQDQRDZYYZYUQVZTIZNRBLFKGSWBNTNJVFLY\x98\xfb\x95\xd4O', b'A\x00\x02\x00@TNWMDSTEGKQHNWFYERIUCQNFIFPCFRISTWCHQLYSYYFRVLDPYWFTIZSZSNMKGJTXc\xcb\x96\xb6O', b'A\x00\x03\x00@PFRSCTKKSYQBHFDRTPGLYMWTUXWMGCGDRUXHZZUZGEYXPBLHBZEYCELGZTPQWYMN\xd3\x85\x0f\xa6O', b'A\x00\x04\x00@SXLMGVSSHDPENQZUQKSMYRYZNKTFLPHGHLMTRPNKFJJISVEWXDDRUJVPPPINSEPI\xd9E\xef^O', b'A\x00\x05\x00@IHQJZKIGRULKSKZBZMXZGTKSFRYIYMWVYGHEZVKPRDKFWUSGBCNJTQEWDPERCVFG\xaa\x0f\xac\xe5O', b'A\x00\x06\x00@GZWHDZCQLFZLJMLBJWWMPYFHGTRDLPSRVCUZKJWSSYWJKVCWHSDBUERXVUWMHMZZ\xe9\x87\xd3\x81O', b'A\x00\x07\x00@DJCKKMWHNUXGXGVUVGWZPYXZDZYBSVXHBCQEQSQMWEHQCSTNXHXVPNUJDGYSWYPVc\xf44\x06O', b'A\x00\x08\x00@UYKWTUMVKNLPVTICVSBINBGNIEDEDSMRHNDUQVKVDUDQNZBHVSNWTZYZRCMJYCHK\xfe\xd5\x9e>O', b'A\x00\t\x00@QLJTZQUSWPKGSNZSDGGMJIJYQKBJTFILCVHCXIPQRMUWLHFVELWDYYIWBXMFXIQJ\x0c\xfb\xbd>O', b'A\x00\n\x00@ZWPZQMIIWDBXPIVWCJESUZDXPHNNYZECMINEEQLQISZETLVGQUWGDFNDWLUIMTYF\xbe\x03\x10\xe9O', b'A\x00\x0b\x00@QNNFBMGBSMWVDTWMGFFMHMIRNPISGNLPTNGNDMNKZNBDGUEKRFHZFUMVEPGYSIVK\xe1iPNO', b'A\x00\x0c\x00@MJPBDEFBFHEXXMUNXRXGZQVHCSFZCEUHGHEWDWIITBNSVQLULXGIHDJQSDXRRWFQ\x19\x9f\xfe,O', b'A\x00\r\x00@QKQMCLFYXLHGPGITUUCWYFMTLZVEBPCFLJBYGYYTKNDFNMVSJSSETCJRGGRRCEJT\xa0;=gO', b'A\x00\x0e\x00@RHTUBHHGBVRUWCEMTGZBWXCCCVJBTBMZDQXKEHFEHZHTYJWBSYJBVIKDSCBMFMVN3\xc7\x91\xbaO', b'A\x00\x0f\x00@LFZVBFNTSIBVNYVGKETFPTRTRWFWWSJVQPHSNNCKPCFCRFYBDXKTUTZTVFMZQEPN\x95\xd5\xb0|O', b'A\x00\x10\x00@HEUEVWCIMZULSWGMKTVNJHFLPFXPIISYPSUITJXJDTIVBZFXEFYTPTUZILQTENPV\x16\xced\x89O']
DEFAULT_PACKET_LIST_16B = [b'A\x00\x01\x00\x10EBDMPZEZQSJFPMDM\xbf\xfb\x10\xbbO', b'A\x00\x02\x00\x10XMGRPXRSTZHCWHHV\x9c\x7f\xf3\tO', b'A\x00\x03\x00\x10IZTRVLRYKQUEWWVC\x9b,ajO', b'A\x00\x04\x00\x10EHUKBHWHLYKZDHKUj4\x83\xb3O', b'A\x00\x05\x00\x10HBYNPQWPKBIHIFMX."\xfd\xf6O', b'A\x00\x06\x00\x10XRLBENCCWWCQTMEJ\x02\xf8\x1e\xc8O', b'A\x00\x07\x00\x10PBBMQDYHTWREGICU\x1cz\x02\x9fO', b'A\x00\x08\x00\x10MTBFCPUXZXBRHUUPjPZ\x95O', b'A\x00\t\x00\x10XVTDKRZPUSNDBEHK&\x02~\x04O', b'A\x00\n\x00\x10FIIZCSEIQPVGVXNY\xae\x17\xc5\x02O', b'A\x00\x0b\x00\x10FHCJFPVBDFSUDWEWf\x0b\xb8\xdbO', b'A\x00\x0c\x00\x10DBIRGPRDEULRGHUYct\xcf0O', b'A\x00\r\x00\x10EHIIHXLRWGQTGKBI\xe4p;\xfdO', b'A\x00\x0e\x00\x10JJQUGEVLIJLENDNIi\xabb\xeeO', b'A\x00\x0f\x00\x10QBINTXLVEXZCIXEJ\xd3\xa8\tmO', b'A\x00\x10\x00\x10EDILDSXHHUSZEYRBf\xdal\xc1O']


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

def create_packet(sequence_number: int, payload_size: int, payload_data: bytes = None) -> bytes:
    """Create a packet with a header, payload of fixed size, and CRC32 checksum."""
    start_marker = b'A'   # Start marker
    end_marker = b'O'     # End marker
    
    # If no payload data is provided, generate random data (capital letters, excluding 'A' and 'O')
    if payload_data is None:
        allowed_characters = string.ascii_uppercase.replace('A', '').replace('O', '')
        payload_data = ''.join(random.choice(allowed_characters) for _ in range(payload_size)).encode('ascii')
    
    # Convert sequence number and length to 2-byte fields
    sequence_number_bytes = sequence_number.to_bytes(2, byteorder='big')
    length_bytes = payload_size.to_bytes(2, byteorder='big')
    
    # Construct the packet without the start/end markers
    packet_body = sequence_number_bytes + length_bytes + payload_data
    
    # Calculate CRC32 checksum on packet body
    checksum = calculate_checksum(packet_body).to_bytes(4, byteorder='big')
    
    # Construct full packet: start_marker + packet_body + checksum + end_marker
    full_packet = start_marker + packet_body + checksum + end_marker
    return full_packet

def generate_packets(payload_size: int, count: int):
    """Generate `count` packets of a specific payload size."""
    packets = []
    for seq_num in range(1, count + 1):
        packet = create_packet(sequence_number=seq_num, payload_size=payload_size)
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
    
def calculate_per(sent_packets,all_received_bytes) -> int:
    # Packet Error Rate calculation (PER)
    error_count = 0
    expected_checksums = get_checksum_list(sent_packets)
    for checksum in expected_checksums:
        if not checksum in all_received_bytes:
            error_count += 1
    try:        
        return error_count/len(sent_packets)
    except ZeroDivisionError:
        return 0


def send_packets_at_defined_speed(transmitter,predefined_packets:list[bytes],number_of_packets_to_send:int,speed:int):
   # assumes that predefined_packets are all the same size
   print(f'sending {len(predefined_packets[0])}B packets at {speed} packets/s ')
   for i in range(number_of_packets_to_send):
        packet_index = i % len(predefined_packets)  # modulo to repeat packets -> this allows to have custom amount of packets e.g. 18
        packet = predefined_packets[packet_index]
        transmitter.write(packet)
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

                
# packets_200B = generate_packets(payload_size=200, count=16)
# packets_64B = generate_packets(payload_size=64, count=16)
# packets_16B = generate_packets(payload_size=16, count=16)
# print(f"DEFAULT_PACKET_LIST_200B = {packets_200B}")
# print(decode_packet(packets_64B[0]))
