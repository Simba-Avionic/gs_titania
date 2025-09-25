import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ==========================
# TEST CONFIGURATION - EXTENDED
# ==========================

# Odległości (km) do testów
TEST_DISTANCES = [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4]

# --------------------------
# Test1: AIR_SPEED variation
# --------------------------
TEST_1_AIRSPEEDS = [32, 64, 128, 250]       # reprezentatywne prędkości
TEST_1_TRANSMIT_RATES = [1, 8, 15]          # realistyczne transmit_rates (packets per second)

# --------------------------
# Test2: BANDWIDTH / MAX_FREQ variation
# --------------------------
TEST_2_MAX_FREQ = [433080, 433270, 433870]  # ograniczone do 3 wartości
TEST_2_TRANSMIT_RATES = [1, 6, 12]          # najważniejsze transmit_rates

# --------------------------
# Test3: BAUD_RATE / SERIAL_SPEED
# --------------------------
TEST_3_BAUD_RATE = [57600, 115200]          # praktyczne prędkości portu szeregowego
TEST_3_SERIAL_SPEED = [57, 115]             # dopasowane do baud_rate
TEST_3_TRANSMIT_RATES = [1, 4, 12]          # realistyczne transmit_rates

# --------------------------
# Test4: NUM_CHANNELS
# --------------------------
TEST_4_NUM_CHANNELS = [10, 42]              # minimum i maksimum
TEST_4_TRANSMIT_RATES = [1, 10]             # najważniejsze transmit_rates

# --------------------------
# Test5: DUTY_CYCLE
# --------------------------
TEST_5_DUTY_CYCLE = [30, 60, 100]           # wszystkie wartości istotne
TEST_5_TRANSMIT_RATES = [1, 8, 15]          # najważniejsze transmit_rates

# --------------------------
# Test6: TX_POWER variation
# --------------------------
TEST_6_TX_POWER = [5, 11, 17]               # niska, średnia i maksymalna moc
TEST_6_TRANSMIT_RATES = [1, 8, 15]

# --------------------------
# Test7: ECC on/off
# --------------------------
TEST_7_ECC = [0, 1]                          # wyłączona / włączona korekcja błędów
TEST_7_TRANSMIT_RATES = [1, 8]               # realistyczne transmit_rates

# --------------------------
# Test8: OPPRESEND on/off
# --------------------------
TEST_8_OPPRESEND = [0, 1]                    # retransmisja wyłączona / włączona
TEST_8_TRANSMIT_RATES = [1, 8, 12]

# --------------------------
# Test9: Kombinacja ekstremalna
# --------------------------
# Sprawdzenie granic stabilnej transmisji
TEST_9_AIRSPEED = [250]
TEST_9_TX_POWER = [5]
TEST_9_TRANSMIT_RATE = [15]

TEST_10_TX_POWER = [11, 17, 20]
TEST_10_AIR_SPEED = [16, 32, 64]
TEST_10_ECC = [0, 1]

# --------------------------
# DEFAULT RADIO CONFIG
# --------------------------
DEFAULT_CONFIG_RADIO = {
    # 'S0:FORMAT': 26,  # read-only
    'S1:SERIAL_SPEED': 57, 
    'S2:AIR_SPEED': 96, 
    'S3:NETID': 18, 
    'S4:TXPOWER': 17, 
    'S5:ECC': 0, 
    'S6:MAVLINK': 1, 
    'S7:OPPRESEND': 0, 
    'S8:MIN_FREQ': 434480, 
    'S9:MAX_FREQ': 434520,  
    'S10:NUM_CHANNELS': 5, 
    'S11:DUTY_CYCLE': 100, 
    'S12:LBT_RSSI': 0, 
    'S13:MANCHESTER': 0, 
    'S14:RTSCTS': 0, 
    'S15:MAX_WINDOW': 131
}

# --------------------------
# DEFAULT CONFIG FOR TESTING
# --------------------------
DEFAULT_CONFIG = {
    # "port_receiver": "/dev/ttyUSB0",
    # "port_transmitter": "/dev/ttyUSB1",
    "baud_rate": 57600,
    "transmit_rate": 4,
    "override_rate": 1,
    "show_received_data": False,
    "set_rtscts": False,
    "target_packets_amount": 200
}

