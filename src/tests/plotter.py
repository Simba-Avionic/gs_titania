import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file
df = pd.read_csv("test_baud_57600_receiver.csv")

# Optional: plot mean TRANSMIT_RATE per AIR_SPEED
mean_df = df.groupby("AIR_SPEED")["TRANSMIT_RATE"].mean().reset_index()
plt.figure(figsize=(8, 6))
plt.plot(mean_df["AIR_SPEED"], mean_df["TRANSMIT_RATE"], marker="o", linestyle="-")
plt.title("Average TRANSMIT_RATE per AIR_SPEED")
plt.xlabel("AIR_SPEED")
plt.ylabel("Mean TRANSMIT_RATE")
plt.grid(True)
plt.show()

