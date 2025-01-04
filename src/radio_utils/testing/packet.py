import random
import string
import struct

class Packet:
    def __init__(self, packet_length, start_symbol=0x41, end_symbol=0x4F):
        """Initialize Packet with a specified length and custom start/end symbols."""
        self.packet_length = packet_length
        self.start_symbol = start_symbol  # Start with 'A' (0x41)
        self.end_symbol = end_symbol      # End with 'O' (0x4F)

    def generate_packet(self):
        """Generate a single packet with a specified length, start/end symbols, and checksum."""
        
        # Calculate the payload length (total length minus the non-payload bytes)
        payload_length = self.packet_length - 2  # 1 byte for start symbol, 1 byte for end symbol
        
        # Generate random payload of 'payload_length' bytes, ensuring no 'A' (0x41) or 'O' (0x4F)
        payload = ''.join(random.choices(string.ascii_uppercase + string.digits, k=payload_length))
        
        # Ensure 'A' and 'O' are not in the payload
        payload = payload.replace('A', 'B').replace('O', 'P')
        payload = payload.encode('utf-8')
        
        # Construct the packet: [start symbol] + [payload] + [checksum] + [end symbol]
        packet_without_checksum = bytes([self.start_symbol]) + payload
        packet = packet_without_checksum + bytes([self.end_symbol]) # removed checksum because it seems that mavlink struggles sometimes to decode hex decimals in \xef format

        return packet

    @staticmethod
    def generate_packet_array(num_packets, packet_length):
        """Generate an array of packets with the requested length."""
        packet_array = []
        for _ in range(num_packets):
            packet = Packet(packet_length)
            packet_array.append(packet.generate_packet())
        return packet_array