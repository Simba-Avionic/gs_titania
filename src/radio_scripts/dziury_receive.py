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
    # selected_port, detected_baud = radio_utils.pick_pickables()
    selected_port = "/dev/ttyUSB1"
    detected_baud = 57600
    last_seqNum = -1
    last_send_timestamp = 0
    start_pelne = 0
    good_msgs = 0

    send_timestamps = []
    recv_timestamps = []
    lost_timestamps = []
    lost_y = []
    send_y = []
    recv_y = []

    dziury = []
    pelne = []
    try:
        with radio_utils.serial.Serial(selected_port, detected_baud, timeout=1) as ser:  
            ser.flushInput()      
            ser.flushOutput()
            start_time = time()                
            while time() - start_time < 10:
                received_data = receive_data(ser)
                fields = received_data.split(" ")
                if len(fields) < 4:
                    continue
                seqNum = int(fields[1])
                sendTS = int(fields[2])
                if start_pelne == 0:
                    start_pelne = sendTS
                if last_send_timestamp == 0:
                    last_send_timestamp = sendTS
                if last_seqNum == -1:
                    last_seqNum = seqNum-1
                send_timestamps.append(sendTS)
                recv_timestamps.append(int(time()*1000))
                recv_y.append(seqNum)
                send_y.append(seqNum)
                good_msgs += 1
                if (last_seqNum+1 != seqNum):
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
                last_send_timestamp = sendTS

            dziury_avg = sum(dziury)/len(dziury)
            pelne_avg = sum(pelne)/len(pelne)
            print("Dziury:", dziury, "avg:", dziury_avg)
            print("Pelne:", pelne, "avg:", pelne_avg)
            plt.plot(send_timestamps, send_y, "b.")
            plt.plot(recv_timestamps, recv_y, "g.")
            plt.plot(lost_timestamps, lost_y, "r.")
            plt.show()
    except radio_utils.serial.SerialException as e:
        print(f'Error: {e}')
    except Exception as e:
        print(f'Unexpected error: {e}')

if __name__ == '__main__':
    main()
    