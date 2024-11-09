import sys
import os
# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import radio_utils
from time import time
import matplotlib.pyplot as plt

def send_data(serial_conn, data):
    return serial_conn.write(data)

def receive_data(serial_conn) -> str:
    buff = ""
    while True:
        byte = serial_conn.read()
        if byte == b'':
            continue
        if byte == b'G':
            buff = ""
        buff = buff + byte.decode()
        if byte == b'S':
            return buff

def main():
    # Check if MAX_FREQ is provided as a command-line argument
    if len(sys.argv) > 1:
        selected_port = sys.argv[1]
        min_freq = int(sys.argv[2])
        max_freq = int(sys.argv[3])
        reading_period = int(sys.argv[4]) # how long messages are read 
        sending_frequency = int(sys.argv[5]) #how often message is send
        air_speed = int(sys.argv[6])
        detected_baud = 57600

    else:
        # selected_port, detected_baud = radio_utils.pick_pickables()
        selected_port = "COM5"
        detected_baud = 57600
        reading_period = 7
        
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
    total_bytes_sent_until_fail = 0
    first_wrong_found = False

    dziury = []
    pelne = []
    try:
        with radio_utils.serial.Serial(selected_port, detected_baud, timeout=1) as ser:  
            ser.flushInput()      
            ser.flushOutput()
            start_time = time()                
            while time() - start_time < reading_period:
                received_data = receive_data(ser)
                time_ms = int(time()*1000)
                if received_data[0:2] != "G " or received_data[-2:] != " S":
                    print("Incorrect start and end of message:", received_data)
                    if wrong_y_val != 0:
                        wrong_timestamps.append(time_ms)
                        wrong_y_val += 1
                        wrong_y.append(wrong_y_val)
                    continue
                fields = received_data.split(" ")
                if len(fields) < 5 or '' in fields:
                    print("Incorrect number of fields:", received_data)
                    if wrong_y_val != 0:
                        wrong_timestamps.append(time_ms)
                        wrong_y_val += 1
                        wrong_y.append(wrong_y_val)
                    continue
                seqNum = int(fields[1])
                sendTS = int(fields[2])
                
                checksum = seqNum + sendTS
                if checksum != int(fields[3]):
                    print("Incorrect checksum:", received_data)
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
                    last_seqNum = seqNum-1
                    wrong_y_val = seqNum-1
                send_timestamps.append(sendTS)
                recv_timestamps.append(int(time()*1000))
                recv_y.append(seqNum)
                send_y.append(seqNum)
                
                if not first_wrong_found:
                    # Calculate bytes sent (for simplicity, assume each message is sent as a string of chars)
                    message = f"G {seqNum} {sendTS} {checksum} S"
                    total_bytes_sent_until_fail += len(message.encode('utf-8'))  # Encode the message to get the byte length

                good_msgs += 1
                print(fields)
                if (last_seqNum+1 != seqNum):
                    if not first_wrong_found: first_wrong_found = True

                    num_of_lost_messages = seqNum-last_seqNum-1
                    dziura_ts = sendTS - last_send_timestamp
                    dziury.append(dziura_ts)
                    delta_ts = dziura_ts / (num_of_lost_messages+1)
                    print("Last ts:", last_send_timestamp%10000, "now ts", sendTS%10000, "last_seq:", last_seqNum, "now_seq:", seqNum, "lost_msgs:", num_of_lost_messages, "delta_ts:", delta_ts)
                    for i in range(num_of_lost_messages):
                        send_timestamps.append(last_send_timestamp + (i+1)*int(delta_ts))
                        lost_timestamps.append(last_send_timestamp + (i+1)*int(delta_ts)+3)
                        send_y.append(last_seqNum+i+1)
                        lost_y.append(last_seqNum+i+1)
                    good_msgs = 0
                    pelne.append(last_send_timestamp-start_pelne)
                    start_pelne = sendTS
                last_seqNum = seqNum
                wrong_y_val = seqNum
                last_send_timestamp = sendTS

            if len(dziury) > 0:
                dziury_avg = sum(dziury)/len(dziury)
                pelne_avg = sum(pelne)/len(pelne)
                print("Dziury:", dziury, "avg:", dziury_avg)
                print("Pelne:", pelne, "avg:", pelne_avg)
            plt.plot(send_timestamps, send_y, "b.",)
            plt.plot(recv_timestamps, recv_y, "g.")
            plt.plot(lost_timestamps, lost_y, "r.")
            plt.plot(wrong_timestamps, wrong_y, "y.")
            if len(sys.argv) > 1:
                if not first_wrong_found:
                    total_bytes_sent_until_fail = "N/A"
                # if lost_timestamps[0] is None:
                    # first_lost = lost_timestamps[0]-send_timestamps[0]
                # else:
                    # first_lost = None
                plt.title(str(air_speed) + 'kbps ' + str(sending_frequency)+'Hz '+'min_f: '+str(min_freq)+' max_f: '+str(max_freq)+' bytes sent till lost: ' + str(total_bytes_sent_until_fail) + ' bytes',fontsize = 8) # str(send_timestamps[0]-lost_timestamps[0]
                plt.savefig(str(air_speed) + 'kbps_' + str(reading_period)+'s_'+ str(sending_frequency)+'Hz_'+'min_f_'+str(min_freq)+'_max_f_'+str(max_freq))
            else:
                plt.show()
    except radio_utils.serial.SerialException as e:
        print(f'Error: {e}')
    except Exception as e:
        print(f'Unexpected error: {e}')

if __name__ == '__main__':
    main()
    