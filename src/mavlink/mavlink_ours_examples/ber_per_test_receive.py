from pymavlink import mavutil

# Works properly until 100th packet - assumes that packet_id is two digits so PER gets funky 

# Initialize MAVLink connection on the receiving radio
mavlink_receiver = mavutil.mavlink_connection('COM7', baud=57600)

# Counters for BER and PER
total_bits = 0
bit_errors = 0
total_packets = 0
packet_errors = 0
expected_packet_id = 0

def calculate_bit_errors(sent, received):
    return sum(1 for s, r in zip(sent, received) if s != r)

try:
    while True:
        msg = mavlink_receiver.recv_match(type='STATUSTEXT', blocking=True) # status have a payload up to 100B
        if msg:
            received_payload = msg.text.encode('utf-8')
            print(f"Received packet: {received_payload}")

            # Extract packet ID to match with expected sequence
            received_packet_id = int(received_payload[:2].decode('utf-8'))
            expected_payload = f"{received_packet_id:02}".encode('utf-8') + received_payload[2:50]

            # Update counters
            total_packets += 1
            total_bits += 50 * 8  # 50 bytes = 400 bits

            # Check for packet errors
            if received_packet_id != expected_packet_id:
                print(f"Packet error: Expected {expected_packet_id}, but got {received_packet_id}")
                packet_errors += 1
            else:
                bit_errors_in_packet = calculate_bit_errors(expected_payload, received_payload)
                bit_errors += bit_errors_in_packet

                if bit_errors_in_packet > 0:
                    packet_errors += 1

            # Update expected packet ID
            expected_packet_id += 1

            # Calculate and print BER and PER
            ber = bit_errors / total_bits if total_bits > 0 else 0
            per = packet_errors / total_packets if total_packets > 0 else 0
            print(f"BER: {ber:.6f}, PER: {per:.6f}")

except KeyboardInterrupt:
    print("Receiver script interrupted. Exiting...")
    print(f"Final BER: {bit_errors / total_bits if total_bits > 0 else 0:.6f}")
    print(f"Final PER: {packet_errors / total_packets if total_packets > 0 else 0:.6f}")