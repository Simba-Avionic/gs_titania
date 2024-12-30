import sys
import os
# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import radio_utils.radio_utils as radio_utils
from time import time
import matplotlib.pyplot as plt



def send_data(serial_conn, data):
    return serial_conn.write(data)

def receive_data(serial_conn) -> str:
    """Receives data from serial connection, expecting 50-byte messages ending in 'S'."""
    buff = ""
    while True:
        byte = serial_conn.read()
        if byte == b'':
            continue
        if byte == b'G':  # Message starts with 'G'
            buff = ""
        try:  # Handle decoding errors
            buff += byte.decode()
        except:
            pass
        if len(buff) == 50 and buff.endswith("S"):  # Full 50-byte message received
            return buff

def main():
    if len(sys.argv) > 1:
        selected_port = sys.argv[1]
        min_freq = int(sys.argv[2])
        max_freq = int(sys.argv[3])
        reading_period = int(sys.argv[4])  # Message read duration in seconds
        sending_frequency = int(sys.argv[5])  # Messages sent per second
        air_speed = int(sys.argv[6])
    else:
        selected_port = "COM5"
        reading_period = 7

    detected_baud = 57600

    last_seqNum = -1
    last_send_timestamp = 0
    start_pelne = 0
    good_msgs = 0

    send_timestamps = []
    recv_timestamps = []
    lost_timestamps = []
    wrong_timestamps = []
    lost_y = []
    send_y = []
    recv_y = []
    wrong_y = []
    wrong_y_val = 0
    total_bytes_received = 0
    first_wrong_found = False

    dziury = []
    pelne = []

    try:
        with radio_utils.serial.Serial(selected_port, detected_baud, timeout=0.000001) as ser:
            ser.flushInput()
            ser.flushOutput()
            start_time = time()

            while time() - start_time < reading_period:
                received_data = receive_data(ser)
                time_ms = int(time() * 1000)

                if received_data[0:2] != "G " or not received_data.endswith("S"):
                    # print("Incorrect message format:", received_data)
                    if wrong_y_val != 0:
                        wrong_timestamps.append(time_ms)
                        wrong_y_val += 1
                        wrong_y.append(wrong_y_val)
                    continue

                fields = received_data.split(" ")
                if len(fields) < 5 or '' in fields:
                    # print("Incorrect number of fields:", received_data)
                    if wrong_y_val != 0:
                        wrong_timestamps.append(time_ms)
                        wrong_y_val += 1
                        wrong_y.append(wrong_y_val)
                    continue

                seqNum = int(fields[1])
                sendTS = int(fields[2])
                checksum = seqNum + sendTS

                if checksum != int(fields[3]):
                    # print("Incorrect checksum:", received_data)
                    if wrong_y_val != 0:
                        wrong_timestamps.append(time_ms)
                        wrong_y_val += 1
                        wrong_y.append(wrong_y_val)
                    continue

                if start_pelne == 0:
                    start_pelne = sendTS
                if last_send_timestamp == 0:
                    last_send_timestamp = sendTS
                if last_seqNum == -1:
                    last_seqNum = seqNum - 1
                    wrong_y_val = seqNum - 1

                send_timestamps.append(sendTS)
                recv_timestamps.append(int(time() * 1000))
                recv_y.append(seqNum)
                send_y.append(seqNum)

                total_bytes_received += len(received_data.encode('utf-8'))
                


                # print(fields)

                good_msgs += 1
                if (last_seqNum + 1 != seqNum):
                    print(f'{last_seqNum} | {seqNum}')
                    if not first_wrong_found: first_wrong_found = True

                    num_of_lost_messages = seqNum - last_seqNum - 1
                    dziura_ts = sendTS - last_send_timestamp
                    dziury.append(dziura_ts)
                    delta_ts = dziura_ts / (num_of_lost_messages + 1)
                    print("Last ts:", last_send_timestamp % 10000, "now ts", sendTS % 10000, "last_seq:", last_seqNum, "now_seq:", seqNum, "lost_msgs:", num_of_lost_messages, "delta_ts:", delta_ts)

                    for i in range(num_of_lost_messages):
                        send_timestamps.append(last_send_timestamp + (i + 1) * int(delta_ts))
                        lost_timestamps.append(last_send_timestamp + (i + 1) * int(delta_ts) + 3)
                        send_y.append(last_seqNum + i + 1)
                        lost_y.append(last_seqNum + i + 1)
                    
                    good_msgs = 0
                    pelne.append(last_send_timestamp - start_pelne)
                    start_pelne = sendTS
                last_seqNum = seqNum
                wrong_y_val = seqNum
                last_send_timestamp = sendTS

            if len(dziury) > 0:
                dziury_avg = sum(dziury) / len(dziury)
                pelne_avg = sum(pelne) / len(pelne)
                print("Dziury:", dziury, "avg:", dziury_avg)
                print("Pelne:", pelne, "avg:", pelne_avg)

            plt.plot(send_timestamps, send_y, "b.", label="Sent Messages")
            plt.plot(recv_timestamps, recv_y, "g.", label="Received Messages")
            plt.plot(lost_timestamps, lost_y, "r.", label="Lost Messages")
            plt.plot(wrong_timestamps, wrong_y, "y.", label="Incorrect Messages")
            if len(lost_timestamps) > 0:
                first_loss_after = lost_timestamps[0] - send_timestamps[0]
                first_loss_seq = lost_y[0]
            else:
                first_loss_after = 0
                if len(lost_y) == 0:
                    first_loss_seq = 0
                else:    
                    first_loss_seq = lost_y[0]
                
            if 50*sending_frequency > detected_baud/10:
                additional_text = f't_spd: {50*sending_frequency} B/s (more than Baud)\nmessages_sent: {len(send_y)}\nmessages received: {len(recv_y)}\nmessages lost: {len(lost_y)}\nbaud rate used: {detected_baud}\nfirst loss after: {first_loss_after} ms\nfirst message lost: {first_loss_seq}'
            else:
                additional_text = f't_spd: {50*sending_frequency} B/s\nmessages_sent: {len(send_y)}\nmessages received: {len(recv_y)}\nmessages lost: {len(lost_y)}\nbaud rate used: {detected_baud}\nfirst loss after: {first_loss_after} ms\nfirst message lost: {first_loss_seq}'
            plt.text(0.05, 0.95, additional_text, ha='left', va='top', transform=plt.gca().transAxes, fontsize=8, bbox=dict(facecolor='white', alpha=0.7, edgecolor='black', boxstyle='round,pad=0.5'))
            plt.legend()
            plt.xlabel("Timestamp (ms)")
            plt.ylabel("Sequence Number")
            plt.title(f'a_spd: {air_speed} kb/s;  t_spd: {sending_frequency} messages/s; min_f: {min_freq}; max_f: {max_freq}', fontsize=10)

            if len(sys.argv) > 1:
                # Save the plot with a filename based on parameters
                plot_filename = f'{air_speed}kbps_{reading_period}s_{sending_frequency}Hz_minf_{min_freq}_maxf_{max_freq}.png'
                plt.savefig(plot_filename)
                print(f'Plot saved as {plot_filename}')
            else:
                plt.show()

            output_filename = 'lost_timestamps.txt'
            # Open the file in write mode ('w'). If the file doesn't exist, it will be created.
            with open(output_filename, 'w') as file:
            # Write a header for clarity (optional)
                file.write("Lost Timestamps:\n")
                
                # Write each timestamp from lost_timestamps on a new line
                for timestamp in lost_timestamps:
                    file.write(f"{timestamp}\n")

    except radio_utils.serial.SerialException as e:
        print(f'Error: {e}')
    # except Exception as e:
        # print(f'Unexpected error: {e}')

if __name__ == '__main__':
    main()