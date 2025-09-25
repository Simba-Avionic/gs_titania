import pandas as pd
import matplotlib.pyplot as plt

# Wczytaj CSV
tx_df = pd.read_csv('test_baud_57600_transmitter.csv')
rx_df = pd.read_csv('test_baud_57600_receiver.csv')

# Konwersja kolumn do NumPy arrays
tx_transmit_rate = tx_df['TRANSMIT_RATE'].to_numpy()
tx_l_rssi = tx_df['L_RSSI'].to_numpy()
tx_r_rssi = tx_df['R_RSSI'].to_numpy()
tx_l_noise = tx_df['L_NOISE'].to_numpy()
tx_r_noise = tx_df['R_NOISE'].to_numpy()
tx_per = tx_df['PER'].to_numpy()

rx_transmit_rate = rx_df['TRANSMIT_RATE'].to_numpy()
rx_l_rssi = rx_df['L_RSSI'].to_numpy()
rx_r_rssi = rx_df['R_RSSI'].to_numpy()
rx_l_noise = rx_df['L_NOISE'].to_numpy()
rx_r_noise = rx_df['R_NOISE'].to_numpy()
rx_per = rx_df['PER'].to_numpy()

# Wykres RSSI
plt.figure(figsize=(10,6))
plt.plot(tx_transmit_rate, tx_l_rssi, 'o-', label='TX L_RSSI')
plt.plot(tx_transmit_rate, tx_r_rssi, 'o--', label='TX R_RSSI')
plt.plot(rx_transmit_rate, rx_l_rssi, 's-', label='RX L_RSSI')
plt.plot(rx_transmit_rate, rx_r_rssi, 's--', label='RX R_RSSI')
plt.xlabel('Transmit Rate')
plt.ylabel('RSSI')
plt.title('RSSI vs Transmit Rate')
plt.legend()
plt.grid(True)
plt.show()

# Wykres Noise
plt.figure(figsize=(10,6))
plt.plot(tx_transmit_rate, tx_l_noise, 'o-', label='TX L_NOISE')
plt.plot(tx_transmit_rate, tx_r_noise, 'o--', label='TX R_NOISE')
plt.plot(rx_transmit_rate, rx_l_noise, 's-', label='RX L_NOISE')
plt.plot(rx_transmit_rate, rx_r_noise, 's--', label='RX R_NOISE')
plt.xlabel('Transmit Rate')
plt.ylabel('Noise')
plt.title('Noise vs Transmit Rate')
plt.legend()
plt.grid(True)
plt.show()

# Wykres PER
plt.figure(figsize=(10,6))
plt.plot(tx_transmit_rate, tx_per, 'o-', label='TX PER')
plt.plot(rx_transmit_rate, rx_per, 's-', label='RX PER')
plt.xlabel('Transmit Rate')
plt.ylabel('Packet Error Rate (%)')
plt.title('PER vs Transmit Rate')
plt.legend()
plt.grid(True)
plt.show()
