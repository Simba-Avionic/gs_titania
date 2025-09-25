import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import math
import csv
import os
import sys
import datetime
import serial.tools.list_ports as list_ports

from test_config import (
    DEFAULT_CONFIG,
    DEFAULT_CONFIG_RADIO,
    TEST_1_AIRSPEEDS, TEST_1_TRANSMIT_RATES,
    TEST_2_MAX_FREQ, TEST_2_TRANSMIT_RATES,
    TEST_3_BAUD_RATE, TEST_3_SERIAL_SPEED, TEST_3_TRANSMIT_RATES,
    TEST_4_NUM_CHANNELS, TEST_4_TRANSMIT_RATES,
    TEST_5_DUTY_CYCLE, TEST_5_TRANSMIT_RATES,
    TEST_6_TX_POWER, TEST_6_TRANSMIT_RATES,
    TEST_7_ECC, TEST_7_TRANSMIT_RATES,
    TEST_8_OPPRESEND, TEST_8_TRANSMIT_RATES,
    TEST_9_AIRSPEED, TEST_9_TX_POWER, TEST_9_TRANSMIT_RATE,
    TEST_10_TX_POWER, TEST_10_AIR_SPEED, TEST_10_ECC
)

import radio_utils.testing.testing as testing
import radio_utils.radio_utils as radio_utils
from radio_scripts.change_baud import change_baud

DISTANCES = [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4]


# ------------------------------
# BACKEND – funkcje narzędziowe
# ------------------------------
def generate_csv_filename(test_name, distance):
    os.makedirs("results", exist_ok=True)  # create folder if it doesn't exist
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{test_name}_{distance}km_{timestamp}.csv"
    return os.path.join("results", filename)  # save inside results/

def scan_serial_ports():
    ports = []
    for p in list_ports.comports():
        name = p.device or ""
        desc = (p.description or "").upper()

        if "USB" in name.upper() or "ACM" in name.upper() or "USB" in desc:
            ports.append(name)

        elif sys.platform.startswith("win") and name.upper().startswith("COM"):
            ports.append(name)

    return ports if ports else ["<no USB/ACM/COM ports>"]


def save_csv_row(data: dict, csv_file):
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)


def run_test(port, is_receiver: bool, on_update=None):
    node = testing.MAVTestNode(port, DEFAULT_CONFIG, DEFAULT_CONFIG_RADIO, is_receiver=is_receiver)
    node.run(on_update=on_update)
    node.close_connection()
    return node



def change_baud_wrapper(port, initial_baud_rate, new_baud_rate):
    if initial_baud_rate in (None, 0):
        initial_baud_rate = radio_utils.detect_baud_rate(port)
    if new_baud_rate == math.floor(initial_baud_rate / 1000):
        return
    change_baud(first_port=port, initial_baud_rate=initial_baud_rate, new_baud_rate=new_baud_rate)


def read_radio_config(port):
    try:
        radio = radio_utils.RadioModule(port, DEFAULT_CONFIG["baud_rate"])
        cfg = radio.get_current_parameters()
        radio.leave_command_mode()
        radio.close()
        return cfg
    except Exception as e:
        return {"error": str(e)}


def reset_radio(port):
    radio_utils.reboot_radios(port, 57600)




# ------------------------------
# TKINTER – GUI
# ------------------------------
class MAVTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MAVTest GUI – Telemetry Logging")

        # --- Zmienne ---
        self.role = tk.StringVar(value="Transmitter")
        self.selected_test = tk.StringVar(value="test_1")
        self.selected_distance = tk.DoubleVar(value=1.0)
        self.port = tk.StringVar(value="")
        self.status_text = tk.StringVar(value="Idle")
        self.stats_text = tk.StringVar(value="Stats: ---")
        self.elapsed_time_text = tk.StringVar(value="Elapsed: 0s")


        # --- Górny panel ---
        top_frame = tk.Frame(root)
        top_frame.pack(pady=10)

        ttk.Label(top_frame, text="Role:").grid(row=0, column=0, padx=5)
        ttk.Combobox(top_frame, textvariable=self.role, values=["Transmitter", "Receiver"], width=15).grid(row=0, column=1, padx=5)

        ttk.Label(top_frame, text="Test:").grid(row=0, column=2, padx=5)
        tests = ["test_1","test_2","test_3","test_4","test_5","test_6","test_7","test_8","test_9", "test_10"]
        ttk.Combobox(top_frame, textvariable=self.selected_test, values=tests, width=10).grid(row=0, column=3, padx=5)

        ttk.Label(top_frame, text="Distance [km]:").grid(row=0, column=4, padx=5)
        ttk.Combobox(top_frame, textvariable=self.selected_distance, values=DISTANCES, width=5).grid(row=0, column=5, padx=5)

        ttk.Label(top_frame, text="Serial Port:").grid(row=0, column=6, padx=5)
        self.port_box = ttk.Combobox(top_frame, textvariable=self.port, values=scan_serial_ports(), width=18)
        self.port_box.grid(row=0, column=7, padx=5)
        ttk.Button(top_frame, text="Rescan", command=self.rescan_ports).grid(row=0, column=8, padx=5)

        ttk.Button(top_frame, text="Run Test", command=self.start_test).grid(row=0, column=9, padx=5)
        ttk.Button(top_frame, text="Reset Radio", command=self.reset_radio).grid(row=0, column=10, padx=5)

        # --- Dolny panel ---
        bottom_frame = tk.Frame(root)
        bottom_frame.pack(padx=10, pady=10, fill="both", expand=True)

        bottom_frame.columnconfigure(0, weight=1)
        bottom_frame.columnconfigure(1, weight=3)

        config_frame = tk.LabelFrame(bottom_frame, text="Live Statistics / Config")
        config_frame.grid(row=0, column=0, sticky="nsew", padx=(0,10))
        self.config_display = tk.Text(config_frame, height=20, font=("Courier", 8))
        self.config_display.pack(fill="both", expand=True, padx=5, pady=5)
        ttk.Button(config_frame, text="Refresh Config", command=self.refresh_config).pack(pady=5)

        stats_frame = tk.LabelFrame(bottom_frame, text="Status")
        stats_frame.grid(row=0, column=1, sticky="nsew")
        ttk.Label(stats_frame, textvariable=self.status_text, anchor="w").pack(fill="x", padx=10, pady=5)
        ttk.Label(stats_frame, textvariable=self.stats_text, anchor="w").pack(fill="x", padx=10, pady=5)
        ttk.Label(stats_frame, textvariable=self.elapsed_time_text, anchor="w").pack(fill="x", padx=10, pady=5)


        self.refresh_config()

    # --------------------------
    def rescan_ports(self):
        ports = scan_serial_ports()
        self.port_box["values"] = ports
        if ports:
            self.port.set(ports[0])

    def refresh_config(self):
        p = self.port.get()
        if not p or p.startswith("<"):
            self.config_display.delete(1.0, tk.END)
            self.config_display.insert(tk.END, "No valid port selected.")
            return
        cfg = read_radio_config(p)
        self.config_display.delete(1.0, tk.END)
        if "error" in cfg:
            self.config_display.insert(tk.END, f"Error: {cfg['error']}")
        else:
            for k,v in cfg.items():
                self.config_display.insert(tk.END, f"{k}: {v}\n")

    def reset_radio(self):
        p = self.port.get()
        if not p or p.startswith("<"):
            messagebox.showerror("Error", "Select a valid port first.")
            return
        try:
            reset_radio(p)
            messagebox.showinfo("Info", "Radio has been reset to default.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def start_test(self):
        p = self.port.get()
        if not p or p.startswith("<"):
            messagebox.showerror("Error", "Select a valid serial port first.")
            return
        test_name = self.selected_test.get()
        is_receiver = (self.role.get() == "Receiver")
        self.status_text.set(f"Running {test_name} as {self.role.get()} ...")

        t = threading.Thread(target=self.run_selected_test, args=(test_name, is_receiver))
        t.daemon = True
        t.start()

    def log_node_stats(self, stats, distance, test_name, csv_file):
        """Callback to save stats every second during the test."""
        csv_data = {
            "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
            "test_name": test_name,
            "role": self.role.get(),
            "distance_km": distance,
            "SERIAL_SPEED": DEFAULT_CONFIG_RADIO.get("S1:SERIAL_SPEED"),
            "AIR_SPEED": DEFAULT_CONFIG_RADIO.get("S2:AIR_SPEED"),
            "NETID": DEFAULT_CONFIG_RADIO.get("S3:NETID"),
            "TX_POWER": DEFAULT_CONFIG_RADIO.get("S4:TXPOWER"),
            "ECC": DEFAULT_CONFIG_RADIO.get("S5:ECC"),
            "MAVLINK": DEFAULT_CONFIG_RADIO.get("S6:MAVLINK"),
            "OPPRESEND": DEFAULT_CONFIG_RADIO.get("S7:OPPRESEND"),
            "MIN_FREQ": DEFAULT_CONFIG_RADIO.get("S8:MIN_FREQ"),
            "MAX_FREQ": DEFAULT_CONFIG_RADIO.get("S9:MAX_FREQ"),
            "NUM_CHANNELS": DEFAULT_CONFIG_RADIO.get("S10:NUM_CHANNELS"),
            "DUTY_CYCLE": DEFAULT_CONFIG_RADIO.get("S11:DUTY_CYCLE"),
            "LBT_RSSI": DEFAULT_CONFIG_RADIO.get("S12:LBT_RSSI"),
            "MANCHESTER": DEFAULT_CONFIG_RADIO.get("S13:MANCHESTER"),
            "RTSCTS": DEFAULT_CONFIG_RADIO.get("S14:RTSCTS"),
            "MAX_WINDOW": DEFAULT_CONFIG_RADIO.get("S15:MAX_WINDOW"),
            "TRANSMIT_RATE": DEFAULT_CONFIG.get("transmit_rate"),
            "BAUD_RATE": DEFAULT_CONFIG.get("baud_rate"),
            "L_RSSI": round((stats.module_local_rssi / 1.9) - 127,2),
            "R_RSSI": round((stats.module_remote_rssi / 1.9) - 127,2),
            "L_NOISE": round((stats.module_local_noise / 1.9) - 127,2),
            "R_NOISE": round((stats.module_remote_noise / 1.9) - 127,2),
            "PACKETS_LOST_TOTAL": stats.total_mav_loss,
            "PER": round(stats.per, 2),
            "TX_BUFF": stats.module_txbuf,
        }
        save_csv_row(csv_data, csv_file)
        self.config_display.delete(1.0, tk.END)
        for k, v in csv_data.items():
            self.config_display.insert(tk.END, f"{k}: {v}\n")

        

    def run_selected_test(self, test_name, is_receiver):
        distance = self.selected_distance.get()
        csv_file = generate_csv_filename(test_name, distance)
        start_time = time.time()

        def update_elapsed():
            while getattr(threading.current_thread(), "running", True):
                elapsed = int(time.time() - start_time)
                self.elapsed_time_text.set(f"Elapsed: {elapsed}s")
                time.sleep(1)

        elapsed_thread = threading.Thread(target=update_elapsed)
        elapsed_thread.daemon = True
        elapsed_thread.start()

        try:
            for param_set in self.test_generator(test_name):
                self.stats_text.set(f"{param_set}")

                radio = radio_utils.RadioModule(self.port.get(), DEFAULT_CONFIG["baud_rate"])
                for key, value in param_set.items():
                    if ':' not in key:
                        for radio_key in DEFAULT_CONFIG_RADIO.keys():
                            if radio_key.endswith(key):
                                DEFAULT_CONFIG_RADIO[radio_key] = value
                                break
                    elif key == "TX_RATE":
                        DEFAULT_CONFIG["transmit_rate"] = value
                    elif key == "BAUD":
                        DEFAULT_CONFIG["baud_rate"] = value

                radio.set_params_to_request(DEFAULT_CONFIG_RADIO)
                radio.leave_command_mode()
                radio.close()

                node = run_test(
                    self.port.get(),
                    is_receiver,
                    on_update=lambda stats: self.log_node_stats(stats, distance, test_name, csv_file)
                )

                time.sleep(0.5)

            elapsed_thread.running = False
            self.elapsed_time_text.set(f"Elapsed: {int(time.time() - start_time)}s")
            self.status_text.set("Test finished.")
            self.status_text.set("Test finished.")
        except Exception as e:
            elapsed_thread.running = False
            self.status_text.set(f"Error: {e}")

    # --------------------------
    def test_generator(self, test_name):
        if test_name == "test_1":
            for air_speed in TEST_1_AIRSPEEDS:
                DEFAULT_CONFIG_RADIO['S2:AIR_SPEED'] = air_speed
                for transmit_rate in TEST_1_TRANSMIT_RATES:
                    if transmit_rate * 500 > DEFAULT_CONFIG["baud_rate"]/9.6:
                        continue
                    DEFAULT_CONFIG["transmit_rate"] = transmit_rate
                    yield {"S2:AIR_SPEED": air_speed, "TX_RATE": transmit_rate}

        elif test_name == "test_2":
            for max_freq in TEST_2_MAX_FREQ:
                DEFAULT_CONFIG_RADIO['S9:MAX_FREQ'] = max_freq
                for transmit_rate in TEST_2_TRANSMIT_RATES:
                    if transmit_rate * 500 > DEFAULT_CONFIG["baud_rate"]/9.6:
                        continue
                    DEFAULT_CONFIG["transmit_rate"] = transmit_rate
                    yield {"S9:MAX_FREQ": max_freq, "TX_RATE": transmit_rate}

        elif test_name == "test_3":
            for br in TEST_3_BAUD_RATE:
                DEFAULT_CONFIG["baud_rate"] = br
                for transmit_rate in TEST_3_TRANSMIT_RATES:
                    if transmit_rate * 500 > br/9.6:
                        continue
                    DEFAULT_CONFIG["transmit_rate"] = transmit_rate
                    yield {"BAUD": br, "TX_RATE": transmit_rate}

        elif test_name == "test_4":
            for num_channels in TEST_4_NUM_CHANNELS:
                DEFAULT_CONFIG_RADIO['S10:NUM_CHANNELS'] = num_channels
                for transmit_rate in TEST_4_TRANSMIT_RATES:
                    DEFAULT_CONFIG["transmit_rate"] = transmit_rate
                    yield {"S10:NUM_CHANNELS": num_channels, "TX_RATE": transmit_rate}

        elif test_name == "test_5":
            for duty_cycle in TEST_5_DUTY_CYCLE:
                DEFAULT_CONFIG_RADIO['S11:DUTY_CYCLE'] = duty_cycle
                for transmit_rate in TEST_5_TRANSMIT_RATES:
                    DEFAULT_CONFIG["transmit_rate"] = transmit_rate
                    yield {"S11:DUTY_CYCLE": duty_cycle, "TX_RATE": transmit_rate}

        elif test_name == "test_6":
            for tx_power in TEST_6_TX_POWER:
                DEFAULT_CONFIG_RADIO['S4:TXPOWER'] = tx_power
                for transmit_rate in TEST_6_TRANSMIT_RATES:
                    DEFAULT_CONFIG["transmit_rate"] = transmit_rate
                    yield {"S4:TXPOWER": tx_power, "TX_RATE": transmit_rate}

        elif test_name == "test_10":
            for tx_power in TEST_10_TX_POWER:
                DEFAULT_CONFIG_RADIO['S4:TXPOWER'] = tx_power
                for air_speed in TEST_10_AIR_SPEED:
                    DEFAULT_CONFIG_RADIO['S2:AIR_SPEED'] = air_speed
                    for ecc in TEST_10_ECC:
                        DEFAULT_CONFIG_RADIO["S5:ECC"] = ecc
                        yield {"S4:TXPOWER": tx_power, "S2:AIR_SPEED": air_speed, "S5:ECC": ecc}


# ------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = MAVTestApp(root)
    root.mainloop()
