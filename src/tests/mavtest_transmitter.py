import sys, os, time, threading
# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import queue as Queue

import radio_utils.testing.testing as testing
import radio_utils.radio_utils as radio_utils

from pymavlink import mavutil


# pretty much copied (adapted) from mavtester.py from
# https://github.com/ArduPilot/SiK/blob/50189f2990a95f5a11e246edc750b7e9b6c96591/Firmware/tools/mavtester.py


try:
    # Init serial connection
    # port, baud_rate = radio_utils.pick_pickables()
    transmitter_port = 'COM5'
    baud_rate = 57600 # max_transmit_speed = min(baud_rate/9.6, air_speed)
    transmit_rate = 15  # number of messages per second (1 = 500B/s if everything uncommented in send_telemetry)
    override_rate = 1
    show_received_data = False
    set_rtscts = False


    transmitter = mavutil.mavlink_connection(transmitter_port, baud=baud_rate)

    print("Draining ports")
    transmitter.port.timeout = 1
    # while True:
    #     r = transmitter.port.read(1024)
    #     if not r:
    #         break
    #     print("Drained %u bytes from transmitter" % len(r))
    #     time.sleep(0.01)

    # RTS/CTS protocol is a method of handshaking which uses one wire in each direction to allow each device to indicate to the other whether or not it is ready to receive data at any given moment. 
    transmitter.set_rtscts(set_rtscts) 

    def allow_unsigned(mav, msgId):
        '''see if an unsigned packet should be allowed'''
        allow = {
            mavutil.mavlink.MAVLINK_MSG_ID_RADIO : True,
            mavutil.mavlink.MAVLINK_MSG_ID_RADIO_STATUS : True 
        }
        if msgId in allow:
            return True
        return False

    # we use thread based receive to avoid problems with serial buffer overflow in the Linux kernel. <-- MZ: Big? Try disabling and compare
    def receive_thread(mav, q):
        '''continuously receive packets are put them in the queue'''
        last_pkt = time.time()
        while True:
            m = mav.recv_match(blocking=False)
            if m is not None:
                q.put(m)
                last_pkt = time.time()

    transmitter_queue = Queue.Queue()
    transmitter_thread = threading.Thread(target=receive_thread, args=(transmitter, transmitter_queue))
    transmitter_thread.daemon = True
    transmitter_thread.start()

    # init vars
    start_time = time.time()
    last_transmitter_send = time.time()


    def recv_transmitter():
        '''
        receive packets in the vehicle (transmitter)
        '''
        try:
            m = transmitter_queue.get(block=False)
        except Queue.Empty:
            return False
        if m.get_type() == 'BAD_DATA':
            stats.transmitter_bad_data += 1
            return True
        if show_received_data:
            print(m)
        stats.transmitter_received += 1
        if m.get_type() in ['RADIO','RADIO_STATUS']:
            #print('VRADIO: ', str(m))
            stats.transmitter_radio_received += 1
            stats.transmitter_txbuf = m.txbuf
            stats.transmitter_fixed = m.fixed
            stats.transmitter_rssi = m.rssi
            stats.receiver_rssi = m.remrssi
            stats.transmitter_noise = m.noise
            stats.receiver_noise = m.remnoise
            stats.received_errors = m.rxerrors # count of packet receive errors (sent by receiver)
        return True


    class PacketStats(object):
        '''
        class to hold statistics on the link
        '''
        def __init__(self):
            self.transmitter_sent = 0
            self.transmitter_received = 0
            self.transmitter_radio_received = 0
            self.transmitter_last_bytes_sent = 0
            self.transmitter_bad_data = 0
            self.last_transmitter_radio = None
            self.transmitter_txbuf = 100
            self.transmitter_rssi = 0
            self.receiver_rssi = 0
            self.transmitter_noise = 0
            self.receiver_noise = 0
            self.transmitter_fixed = 0
            self.received_errors = 0

        def __str__(self):
            transmitter_bytes_sent = transmitter.mav.total_bytes_sent - self.transmitter_last_bytes_sent
            self.transmitter_last_bytes_sent = transmitter.mav.total_bytes_sent
            
            return_message = f"""Transmitter 
                Total_Send/Total_Received/Packets_Received: {self.transmitter_sent}/{self.transmitter_received}/{self.transmitter_received - self.transmitter_radio_received}
                bytes_sent:{transmitter_bytes_sent}
                bad_data:{self.transmitter_bad_data}
                txbuf:{self.transmitter_txbuf}
                tx_rssi:{self.transmitter_rssi} tx_noise:{self.transmitter_noise}
                rx_rssi:{self.receiver_rssi} rx_noise:{self.receiver_noise}
                mav_loss:{transmitter.mav_loss} packet_loss:{transmitter.packet_loss()}
                fixed:{self.transmitter_fixed}
                received_errors: {self.received_errors}"""
            return return_message

    '''
    main code
    '''
    last_report = time.time()
    stats = PacketStats()

    while True:

        testing.send_mav_telemetry_500B(transmitter)
        time.sleep(1/transmit_rate)
        stats.transmitter_sent = transmitter.mav.total_packets_sent

        while True:
            recv1 = recv_transmitter()
            if not recv1:
                break

        if time.time() - last_report >= 1.0:
            print(f"time passed since last report: {time.time() - last_report}")
            print(stats)
            last_report = time.time()
except KeyboardInterrupt:
    print("Stops Transmitting...")