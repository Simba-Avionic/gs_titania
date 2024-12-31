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
    port = 'COM8'
    baud_rate = 57600
    override_rate = 1
    show_received_data = False
    set_rtscts = False


    receiver = mavutil.mavlink_connection(port, baud=baud_rate)

    print("Draining ports")
    receiver.port.timeout = 1
    # while True:
    #     r = receiver.port.read(1024)
    #     if not r:
    #         break
    #     print("Drained %u bytes from receiver" % len(r))
    #     time.sleep(0.01)

    # RTS/CTS protocol is a method of handshaking which uses one wire in each direction to allow each device to indicate to the other whether or not it is ready to receive data at any given moment. 
    receiver.set_rtscts(set_rtscts) 

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

    receiver_queue = Queue.Queue()
    receiver_thread = threading.Thread(target=receive_thread, args=(receiver, receiver_queue))
    receiver_thread.daemon = True
    receiver_thread.start()

    # init vars
    start_time = time.time()
    last_receiver_send = time.time()
    last_override_send = time.time()

    def send_GCS():
        '''
        send GCS (receiver) heartbeat messages
        '''
        global last_receiver_send
        now = time.time()
        if now - last_receiver_send < 1.0:
            return
        receiver.mav.heartbeat_send(1, 6, 0, 0, 0, 0)
        last_receiver_send = now

    # MZ: idk
    def send_override():
        '''
        send RC_CHANNELS_OVERRIDE messages from GCS (receiver)
        '''
        global last_override_send
        now = time.time()
        if override_rate == 0:
            return
        if now - last_override_send < 1.0/override_rate:
            return
        time_ms = int((now - start_time) * 1.0e3)
        time_ms_low  = time_ms % 65536
        time_ms_high = (time_ms - time_ms_low) // 65536
        receiver.mav.rc_channels_override_send(1, 2, time_ms_low, time_ms_high, 0, 0, 0, 0, 0, 0)
        last_override_send = now

    def recv_GCS():
        '''
        receive packets in the GCS (receiver)
        '''
        try:
            m = receiver_queue.get(block=False)
        except Queue.Empty:
            return False
        if m.get_type() == 'BAD_DATA':
            stats.receiver_bad_data += 1
            return True

        if show_received_data:
            print(m)
        stats.receiver_received += 1        
        if m.get_type() in ['RADIO','RADIO_STATUS']:
            #print('GRADIO: ', str(m))
            stats.receiver_radio_received += 1            
            stats.receiver_txbuf = m.txbuf
            stats.receiver_fixed = m.fixed
            stats.receiver_rssi = m.rssi
            stats.transmitter_rssi = m.remrssi
            stats.receiver_noise = m.noise
            stats.transmitter_noise = m.remnoise
            stats.received_errors = m.rxerrors # count of packet receive (sent by transmitter) errors
        return True

    class PacketStats(object):
        '''
        class to hold statistics on the link
        '''
        def __init__(self):
            self.receiver_sent = 0
            self.receiver_received = 0
            self.receiver_radio_received = 0
            self.receiver_last_bytes_sent = 0
            self.receiver_last_bytes_received = 0
            self.receiver_bad_data = 0
            self.last_receiver_radio = None
            self.receiver_txbuf = 100
            self.receiver_rssi = 0
            self.transmitter_rssi = 0
            self.receiver_noise = 0
            self.transmitter_noise = 0
            self.receiver_fixed = 0
            self.received_errors = 0

        def __str__(self):
            receiver_bytes_sent = receiver.mav.total_bytes_sent - self.receiver_last_bytes_sent
            self.receiver_last_bytes_sent = receiver.mav.total_bytes_sent
            receiver_bytes_received = receiver.mav.total_bytes_received - self.receiver_last_bytes_received
            self.receiver_last_bytes_received = receiver.mav.total_bytes_received
            
            return_message = f"""Receiver:
            Total_Send/Total_Received/Packets_Received: {self.receiver_sent}/{self.receiver_received}/{self.receiver_received - self.receiver_radio_received}
            bytes_sent:{receiver_bytes_sent}
            bytes_received:{receiver_bytes_received}
            bad_data:{self.receiver_bad_data}
            txbuf:{self.receiver_txbuf} 
            tx_rssi:{self.transmitter_rssi} tx_noise:{self.transmitter_noise}
            rx_rssi:{self.receiver_rssi} rx_noise:{self.receiver_noise}
            mav_loss:{receiver.mav_loss} packet_loss:{receiver.packet_loss()}
            fixed:{stats.receiver_fixed} 
            received_errors: {self.received_errors}""" 
            return return_message

    '''
    main code
    '''
    last_report = time.time()
    stats = PacketStats()

    while True:


        send_GCS()
        send_override()
        stats.receiver_sent = receiver.mav.total_packets_sent

        while True:
            recv1 = recv_GCS()
            if not recv1:
                break

        if time.time() - last_report >= 1.0:
            print(f"time passed since last report: {time.time() - last_report}")
            print(stats)
            last_report = time.time()
except KeyboardInterrupt:
    print("Stops Receiving...")