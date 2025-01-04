from enum import Enum
import csv, queue, threading, time
from pymavlink import mavutil


PACKETS_ARRAY_LENGTH = 20
# Numbers describe the number of bytes in one package, each list consists of PACKETS_ARRAY_LENGTH packets
DEFAULT_PACKET_LISTS = { 
    10 : [b'AFZBGMH4CO', b'ANYIQ9LPBO', b'AK32BUER4O', b'AMB24H4E6O', b'A1B1YV7BZO', b'ARL2PBZY4O', b'AP3WLXGN2O', b'APKDNPF3NO', b'AQFF0C3TEO', b'AMXD603XKO', b'AGNBPHCK4O', b'AVF9K0NRDO', b'A2X899P4JO', b'APQXQUSK4O', b'ABD2B7P4HO', b'AGYWPEDDMO', b'AZPBTGLIVO', b'AN28JYZU0O', b'AUUZCKL5ZO', b'AZB50TUD4O'],
    20 : [b'AYX37CKR2XI3C3FBQPNO', b'ASNQPBHN27D8CUY63W5O', b'AC3MEP4KBXN8HZPB1DKO', b'A0WN3UX3R7PRHNWP0PPO', b'AR1CNDP2ZDN5CVJDG96O', b'A9G9GR0ISD3JGFEPYBPO', b'AWR615N6UB4MX50DUGYO', b'AGF78K040PPKW9QP11EO', b'AVPFE2B4MJI27ZGRX2PO', b'A0M6YTK99T52MP5ZPRPO', b'AJJGDB5EQ593XCD52XDO', b'ASBR21JNG8LZBLX3E8CO', b'AZ6TV7R8V39X4R1CQCLO', b'AN69SCCZXLFJMN0GDPFO', b'AY03PSW6B34BFDIBXCFO', b'A5JK8CHWKZRBMLRIB2UO', b'AQGZSRSF5GPST737ZGXO', b'ANRZ519UHB5E758HXNRO', b'A6TFYIZK67BVVPX99SHO', b'AJ0TBKVTB2B6NSEQZWTO'],
    44 : [b'AP9HEL87UE1BRYTFXE6Q3TSE860246QEHR8P77TBW79O', b'A30HI7JC6BBRZ8SHF3UF1XT77BXR0C7GTKBXE8BXG1KO', b'A33K5UZCFK14U17RX90V77LY1J4PKVI591SY4M5GHVHO', b'ARQJNMTP84563ZC65Z4P7PMB7SC5EDY965SVN8QIMQTO', b'AVYIGJDXB1INBY8L7TH60L9NDF2G67I4UU4YXGJDPQMO', b'A19Z7N91VVB8FECSYVVXEGY5H7M5PSIIXNK7SM4P8PKO', b'AEBDEHN0PQDSSHFFTTJ8FQ9R691WXBVB56BJ4FC679KO', b'APJPDVPFRBZJ80EVPXRKWJGVFJ1X7VI2BH56WJQRDT7O', b'A47HPC8C5T21DBGD0DZ62XDN3N1R9CLYF4PH2QJYB96O', b'A6GR91WQ4CWHJZCFD3QNJC5340HVKI4QG37BVQGMZU0O', b'A0E2N52WJN6ZB6SHQ2RSSKV5MNNE3PT20D24QN20BB7O', b'A0ILHB3K8ETIK79N0U687BZ5PEF4GP0C06IIBS2KSJQO', b'A22DDP9TVE4PGS0GXHUZVIH2URWZBPBXKNS3M6BII4UO', b'AVIS96K4GLY20XXXWJHPE8DN6PFB2WLT7T88VNUS6W2O', b'AC1M7MTJ2GP2KTPBV14PT9SX37QNUSVCY3FTJEMDD4JO', b'ADBT83SN7JX0XPRQ4T4UU4MJB0846HSFRUY1483PSQPO', b'AUFP5JV3ETXVTBZ20SIFVJTCMIBLVE3XI13PS6RX3NWO', b'AVN7R144UE441BVVZPUM6FLUGLLGQP911C7CIHGU6L7O', b'A946HP0P2DQ2G4BNE7NRLB8YG9U17P8TT1CJT9RBP3ZO', b'AQFSEFDL8H880KXY312PFPT56QPG4B5R0HQ05FL79ZMO'],
    50 : [b'AG3152RDQXW9SCHX9H78M5JXLSZZMYEZ1Y53K4J7RR843BYX4O', b'APE5BBR73MIQ21D3BYJK3K4RYU6ESUTKXIPDD69V3CBBU1XE0O', b'A45UL4R4HRQZWI8I3VFJQ5LG5PJHD1ZBNDK4HUPCMR0VNYU58O', b'A66IRPPEU11MYBVIUVMB02UP8ELKBPV3BICVVG0QYD5IBR41VO', b'AXN71BPPJXYIPBE02FQ8F6GCP82LPF5G64LHRGD7KGY4F14HEO', b'AHBD21QQU9BN7WKXR8B58LBN3SMBM5YG5JQ5GNIGXIPDJ6B2XO', b'AWBHFPQ7TS2TCKUGXFP8TYEJZ1NHRDRV1PQGK7PJIS6E1SE9UO', b'ARC8I8UKH7CISY6NCP34QED8X4BB0BB8G5ZB6RBNI9BJUHRHBO', b'ATHV32SGBG9E7SNFPZFCP7835GMNPC2GEMRDZ7QH6X0PRWT9ZO', b'A6U1K3GT1FEWDRF3D42GGDD51ZD13M3DP5FCYJ7EP1WPNCZK5O', b'AJGMP5FXJ7QYM3MB4HW55UM328RXZYM4ZPLR1I91JHQKHM0SSO', b'A9Q0KL93UL2Q3VR74Q0XX238LDBSWKXG0NBT003CPPTMG86SFO', b'AGF6JU9KE9Q3RERZK61LSJY66LI64QF6WTEK72HJPUMH7PXXXO', b'A5Y8PHQRMK2PKB1DXLFTW9GGQXPBBIX9BQJQQR2BW0GCQRMCJO', b'A4EHGPDPBBRBXYDUMS6U2YPWWEQ82C8N2PSWLDZ6I4YDM6BHFO', b'A93PW8N70W1BH5T2L1NW4IMNUCB6YYPWRPL9BIEB7VB4TBTDSO', b'AJ7F6KNKH6GPFSS9GZCMJ6ZC4YBQZMHZEC3KCE8NYSRWKS60UO', b'ADIMFKP4IBHRG3IYU10WVKPGQMTHDBM69PI1HS2RSI8BXL8CGO', b'ASZ77QJGZPN05VXP7BPD1NLSVY7PH9RBB45NRX2D5BSJYC0RPO', b'A2Z753FXBNG13REYDW0077GWFGIY3JVPD25WIKN6VCBN467BLO']
}

# defines how many packets are to be send for subtest
class TestLength(Enum):
    LONG = 1000
    MEDIUM = 140
    SHORT = 20

def calculate_ber(sent_data, received_data):
    """Calculate the Bit Error Rate (BER) between sent and received data.

    Args:
        sent_data (bytes): The original sent data in bytes.
        received_data (bytes): The received data in bytes.

    Returns:
        float: The calculated BER as a decimal value.
        float: The amount of wrong bits
    """
    if len(sent_data) != len(received_data):
        received_data = received_data.ljust(len(sent_data), b'\0')

    total_bits = len(sent_data) * 8
    bit_errors = sum(bin(s ^ r).count('1') for s, r in zip(sent_data, received_data))

    return bit_errors / total_bits if total_bits > 0 else 0.0, bit_errors

def calculate_per(total_packets, error_packets):
    """Calculate the Packet Error Rate (PER) based on packet error count.

    Args:
        total_packets (int): The total number of packets transmitted.
        error_packets (int): The number of packets received with errors.

    Returns:
        float: The calculated PER as a decimal value.
    """
    if total_packets == 0:
        return 0.0
    return error_packets / total_packets

def save_results_to_csv(output_file_name='results.csv', **kwargs):
    """
    Save results to a CSV file with dynamic headers and values.

    :param output_file_name: Name of the CSV file to write to.
    :param kwargs: Key-value pairs where keys are headers and values are data points.

    Example Usage
    save_results_to_csv(Bandwidth=20,Power_Tx=15,Air_Speed=256,Baud_Rate=9600,Transmit_Speed=50,PER=0.0123,BER=0.0004)
    """

    # Extract headers and values from kwargs
    headers = list(kwargs.keys())
    values = list(kwargs.values())

    # Open the file in append mode
    with open(output_file_name, 'a', newline='') as file:
        writer = csv.writer(file)

        # Check if the file is empty to write headers
        file.seek(0, 2)  # Move to the end of the file
        if file.tell() == 0:  # Check if the file is empty
            writer.writerow(headers)  # Write the headers

        # Write the values
        writer.writerow(values)    


def send_mav_telemetry_500B(transmitter: mavutil.mavlink_connection) -> None:
    '''
    Send telemetry packets from the transmitter to the GCS.
    This emulates the typical pattern of telemetry in ArduPlane 2.75 in AUTO mode.

    The function sends a series of MAVLink messages that together take approximately 500 bytes.

    Parameters:
    transmitter (mavutil.mavlink_connection): 
        A MAVLink connection object used to send telemetry packets.

    Returns:
    None
    '''    
 
    time_usec = int(1 * 1.0e6) 
    time_ms = time_usec // 1000

    transmitter.mav.heartbeat_send(1, 3, 217, 10, 4, 3)
    transmitter.mav.global_position_int_send(time_ms, 3, 1491642131, 737900, 140830, 2008, -433, 224, 35616)
    transmitter.mav.rc_channels_scaled_send(time_boot_ms=time_ms, port=0, chan1_scaled=280, chan2_scaled=3278, chan3_scaled=-3023, chan4_scaled=0, chan5_scaled=0, chan6_scaled=0, chan7_scaled=0, chan8_scaled=0, rssi=0)
    
    transmitter.mav.servo_output_raw_send(time_usec=time_usec, port=0, servo1_raw=1470, servo2_raw=1628, servo3_raw=1479, servo4_raw=1506, servo5_raw=1500, servo6_raw=1556, servo7_raw=1500, servo8_raw=1500)
    transmitter.mav.rc_channels_raw_send(time_boot_ms=time_ms, port=0, chan1_raw=1470, chan2_raw=1618, chan3_raw=1440, chan4_raw=1509, chan5_raw=1168, chan6_raw=1556, chan7_raw=1224, chan8_raw=994, rssi=0)
    transmitter.mav.raw_imu_send(time_usec, 562, 382, -3917, -3330, 3445, 35, -24, 226, -523)
    transmitter.mav.scaled_pressure_send(time_boot_ms=time_ms, press_abs=950.770019531, press_diff=-0.0989062488079, temperature=463)
    transmitter.mav.sensor_offsets_send(mag_ofs_x=-68, mag_ofs_y=-143, mag_ofs_z=-34, mag_declination=0.206146687269, raw_press=95077, raw_temp=463, gyro_cal_x=-0.063114002347, gyro_cal_y=0.0479440018535, gyro_cal_z=0.0190890002996, accel_cal_x=0.418922990561, accel_cal_y=0.284875005484, accel_cal_z=-0.436598002911)
    transmitter.mav.sys_status_send(onboard_control_sensors_present=64559, onboard_control_sensors_enabled=64559, onboard_control_sensors_health=64559, load=82, voltage_battery=11877, current_battery=0, battery_remaining=100, drop_rate_comm=0, errors_comm=0, errors_count1=0, errors_count2=0, errors_count3=0, errors_count4=0)
    transmitter.mav.mission_current_send(seq=1)
    transmitter.mav.gps_raw_int_send(time_usec=time_usec, fix_type=3, lat=-353637616, lon=1491642012, alt=737900, eph=169, epv=65535, vel=2055, cog=34782, satellites_visible=9)
    transmitter.mav.nav_controller_output_send(nav_roll=0.0, nav_pitch=0.319999992847, nav_bearing=-18, target_bearing=343, wp_dist=383, alt_error=-37.0900001526, aspd_error=404.800537109, xtrack_error=1.52732038498)
    transmitter.mav.attitude_send(time_boot_ms=time_ms, roll=0.00283912196755, pitch=-0.0538846850395, yaw=-0.0708072632551, rollspeed=0.226980209351, pitchspeed=-0.00743395090103, yawspeed=-0.154820173979)
    transmitter.mav.vfr_hud_send(airspeed=21.9519939423, groundspeed=20.5499992371, heading=355, throttle=35, alt=737.900024414, climb=-0.784280121326)
    transmitter.mav.ahrs_send(omegaIx=0.000540865410585, omegaIy=-0.00631708558649, omegaIz=0.00380697473884, accel_weight=0.0, renorm_val=0.0, error_rp=0.094664350152, error_yaw=0.0121578350663)
    transmitter.mav.hwstatus_send(Vcc=0, I2Cerr=0)
    transmitter.mav.wind_send(direction=27.729429245, speed=5.35723495483, speed_z=-1.92264056206)

class PacketStats(object):
    '''
    class to hold statistics on the link
    '''
    def __init__(self, moduleObj):
        self.module_sent = 0
        self.module_received = 0
        self.module_radio_received = 0
        self.module_last_bytes_sent = 0
        self.packets_received = 0
        self.total_bytes_sent = 0
        self.module_bytes_sent_now = 0
        self.total_bytes_received = 0
        self.module_bytes_received_now = 0
        self.module_last_bytes_received = 0
        self.module_bad_data = 0
        self.last_module_radio = None
        self.module_txbuf = 100
        self.module_local_rssi = 0
        self.module_remote_rssi = 0
        self.module_local_noise = 0
        self.module_remote_noise = 0
        self.module_fixed = 0
        self.received_errors = 0
        self.total_mav_loss = 0
        self.per = 0

        self.moduleObj = moduleObj
    
    def update_stats(self):
        # Update total values
        self.total_bytes_sent = self.moduleObj.mav.total_bytes_sent
        self.total_bytes_received = self.moduleObj.mav.total_bytes_received
        # Calculate bytes sent/received now
        self.module_bytes_sent_now = self.total_bytes_sent  - self.module_last_bytes_sent
        # print(f'{self.total_bytes_sent}  - {self.module_last_bytes_sent}')
        self.module_bytes_received_now = self.total_bytes_received - self.module_last_bytes_received
        # Update "last" values after the "now" calculation
        self.module_last_bytes_sent = self.total_bytes_sent
        self.module_last_bytes_received = self.total_bytes_received
        
        # Update additional stats
        self.packets_received = self.module_received - self.module_radio_received
        self.total_mav_loss = self.moduleObj.mav_loss
        self.per = self.moduleObj.packet_loss()
    def __str__(self):
        
        
        return_message = f"""    Total_Send/Total_Received/Packets_Received: {self.module_sent}/{self.module_received}/{self.packets_received}
    bytes_sent_now:{self.module_bytes_sent_now}
    bytes_received_now:{self.module_bytes_received_now}
    total_bytes_sent:{self.total_bytes_sent}
    total_bytes_received:{self.total_bytes_received}
    total_bad_data:{self.module_bad_data}
    txbuf:{self.module_txbuf} 
    local_rssi:{self.module_local_rssi} local_noise:{self.module_local_noise}
    remote_rssi:{self.module_remote_rssi} remote_noise: {self.module_remote_noise}
    total_mav_Loss: {self.total_mav_loss} Total_PER: {self.moduleObj.packet_loss()}
    received_errors_total: {self.received_errors}
    fixed: {self.module_fixed}"""
        return return_message
    
class MAVTestNode:
    def __init__(self, config, config_radio, is_receiver=False):
        self.port = config["port_receiver"] if is_receiver else config["port_transmitter"]
        self.baud_rate = config["baud_rate"]
        self.transmit_rate = config.get("transmit_rate", 0)
        self.override_rate = config.get("override_rate", 0)
        self.show_received_data = config["show_received_data"]
        self.set_rtscts = config["set_rtscts"]
        self.is_receiver = is_receiver
        self.target_packets_amount = round(config["target_packets_amount"]*self.transmit_rate*0.8)

        self.air_speed = config_radio["S2:AIR_SPEED"]
        self.power = config_radio["S4:TXPOWER"]
        self.bandwidth = config_radio["S9:MAX_FREQ"] - config_radio["S8:MIN_FREQ"]
        
        # Initialize connection
        self.mavlink = mavutil.mavlink_connection(self.port, baud=self.baud_rate)
        self.mavlink.port.timeout = 0.0001
        self.mavlink.set_rtscts(self.set_rtscts)

        # Initialize variables
        self.last_send_time = time.time()

        # Initialize stats and threads
        self.kill_receiving_thread = False
        self.module_queue, self.thread = self.thread_mav_receive()
        self.stats = PacketStats(self.mavlink)

    def close_connection(self):
        """Clean up the receiving thread and close the MAVLink connection."""
        self.kill_receiving_thread = True
        self.thread.join()  # Ensure thread terminates properly
        self.mavlink.port.close()

    # we use thread based receive to avoid problems with serial buffer overflow in the Linux kernel. <-- MZ: Big? Try disabling and compare
    def thread_mav_receive(self):
        def receive_thread(mav, q):
            '''continuously receive packets and put them in the queue'''
            last_pkt = time.time()
            while True:
                m = mav.recv_match(blocking=False)
                if m is not None:
                    q.put(m)
                    last_pkt = time.time()
                if self.kill_receiving_thread:
                    break

        module_queue = queue.Queue()
        module_thread = threading.Thread(target=receive_thread, args=(self.mavlink, module_queue))
        module_thread.daemon = True
        module_thread.start()
        return module_queue, module_thread

    def receive_mav_packets(self):
        '''
        receive packets 
        '''
        try:
            m = self.module_queue.get(block=False)
        except queue.Empty:
            return False
        if m.get_type() == 'BAD_DATA':
            self.stats.module_bad_data += 1
            return True
        if self.show_received_data:
            print(m)
        self.stats.module_received += 1
        if m.get_type() in ['RADIO','RADIO_STATUS']:
            # print(str(m)) # print RADIO_STATUS
            self.stats.module_radio_received += 1            
            self.stats.module_txbuf = m.txbuf
            self.stats.module_fixed = m.fixed
            self.stats.module_local_rssi = m.rssi
            self.stats.module_remote_rssi = m.remrssi
            self.stats.module_local_noise = m.noise
            self.stats.module_remote_noise = m.remnoise
            self.stats.received_errors = m.rxerrors # count of packet receive (sent by transmitter) errors
        return True
    
    def send_telemetry(self):
        """Send telemetry packets (transmitter-specific)."""
        if not self.is_receiver:
            send_mav_telemetry_500B(self.mavlink)
            time.sleep(1 / self.transmit_rate)

    def send_heartbeat(self):
        """Send heartbeat (receiver-specific)."""
        if self.is_receiver:
            now = time.time()
            if now - self.last_send_time >= 1.0:
                self.mavlink.mav.heartbeat_send(1, 6, 0, 0, 0, 0)
                self.last_send_time = now
    
    def save_stats_to_csv(self,**kwargs):
        csv_name = "test_baud_"+str(self.baud_rate)
        if self.is_receiver:
            csv_name = csv_name + "_receiver.csv"
        else:
            csv_name = csv_name + "_transmitter.csv"
        save_results_to_csv(csv_name,
                        POWER = self.power,
                        BANDWIDTH = self.bandwidth,
                        AIR_SPEED = self.air_speed,
                        TRANSMIT_RATE = self.transmit_rate,
                        BAUD_RATE = self.baud_rate,
                        L_RSSI = self.stats.module_local_rssi,
                        R_RSSI = self.stats.module_remote_rssi,
                        L_NOISE = self.stats.module_local_noise,
                        R_NOISE = self.stats.module_remote_noise,
                        PACKETS_LOST_TOTAL = self.stats.total_mav_loss,
                        PER = self.stats.per,
                        TEMPERATURE = 0
                        )

    def run(self):
        """Main loop for MAVLink node testing."""
        last_report = time.time()
        beginning_of_the_test_time = last_report
        try:
            while True:

                if self.is_receiver:
                    self.send_heartbeat()
                else:
                    self.send_telemetry()
                self.stats.module_sent = self.mavlink.mav.total_packets_sent

                while not self.module_queue.empty():
                    # if self.is_receiver:
                    #     print(f"Receiver queue size: {self.module_queue.qsize()}")
                    # else:
                    #     print(f"Transmitter queue size: {self.module_queue.qsize()}")
                    self.receive_mav_packets()

                if time.time() - last_report >= 1: # print status every second
                    self.stats.update_stats() # threading black magic shenanigans? <--- faster if updated outside the if statement 
                    print(f"{'Receiver' if self.is_receiver else 'Transmitter'} stats: ")
                    print(self.stats)
                    if self.stats.module_bytes_sent_now > 300 or self.stats.module_bytes_received_now > 80: # arbitrary numbers
                        self.save_stats_to_csv()
                    last_report = time.time()

                time.sleep(0.000000001) # threading black magic shenanigans? <---- queue read is instantenious thanks to this
                    
                if self.is_receiver:
                    if (self.stats.packets_received+self.stats.total_mav_loss) >= self.target_packets_amount:
                        break
                else:
                    if self.stats.module_sent >= self.target_packets_amount*1.3:
                        break
            
            self.stats.update_stats()
            print(f"{'Receiver' if self.is_receiver else 'Transmitter'} last stats: ")
            print(self.stats)
            self.save_stats_to_csv()
            test_time = time.time() - beginning_of_the_test_time
            if self.is_receiver:
                print(f"Receiver has reached the target of {self.target_packets_amount} packets (of which {self.stats.total_mav_loss} were lost) received in {test_time}s.")
                print(f'Receive speed: {int(self.stats.total_bytes_received/test_time)}B/s')
            else:
                print(f"Transmitter has reached the target of {self.target_packets_amount*1.3} packets sent in {test_time}s.")
                print(f'Transmission speed: {int(self.stats.total_bytes_sent/test_time)}B/s')

                    
        except KeyboardInterrupt:
            print(f"Stops {'Receiving' if self.is_receiver else 'Transmitting'}...")
            print(f"{'Receiver' if self.is_receiver else 'Transmitter'} last stats: ")
            self.stats.update_stats()
            print(self.stats)
            self.save_stats_to_csv()

