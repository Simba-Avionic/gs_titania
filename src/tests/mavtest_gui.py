import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import math
import csv
import os
import datetime
import serial.tools.list_ports as list_ports

from test_config import (
    DEFAULT_CONFIG,
    DEFAULT_CONFIG_RADIO,
    TEST_1_AIRSPEEDS, TEST_1_TRANSMIT_RATES,
    TEST_2_MAX_FREQ, TEST_2_TRANSMIT_RATES,
    TEST_3_BAUD_RATE, TEST_3_SERIAL_SPEED, TEST_3_TRANSMIT_RATES,
    TEST_4_NUM_CHANNELS, TEST_4_TRANSMIT_RATES,
    TEST_5_DUTY_CYCLE, TEST_5_TRANSMIT_RATES
)

import radio_utils.testing.testing as testing
import radio_utils.radio_utils as radio_utils
from radio_scripts.change_baud import change_baud

CSV_FILE = "mavtest_results.csv"
DISTANCES = [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4]


# ------------------------------
# BACKEND – funkcje narzędziowe
# ------------------------------
def scan_serial_ports():
    ports = []
    for p in list_ports.comports():
        name = p.device
        if "USB" in name.upper() or "ACM" in name.upper() or "USB" in (p.description or "").upper():
            ports.append(name)
    return ports if ports else ["<no USB/ACM ports>"]


def save_csv_row(data: dict):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)


def run_test(is_receiver: bool):
    node = testing.MAVTestNode(DEFAULT_CONFIG, DEFAULT_CONFIG_RADIO, is_receiver=is_receiver)
    node.run()
    node.close_connection()


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


def log_telemetry(port, role="Transmitter"):
    try:
        radio = radio_utils.RadioModule(port, DEFAULT_CONFIG["baud_rate"])
        data = radio.get_output_data()
        if data['temperature'] == -276:
            data = radio.get_output_data()
        radio.leave_command_mode()
        radio.close()

        row = {
            "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
            "role": role,
            "AIR_SPEED": DEFAULT_CONFIG_RADIO.get("S2:AIR_SPEED"),
            "TX_POWER": DEFAULT_CONFIG_RADIO.get("S4:TXPOWER"),
            "BANDWIDTH": DEFAULT_CONFIG_RADIO.get("S9:MAX_FREQ") - DEFAULT_CONFIG_RADIO.get("S8:MIN_FREQ"),
            "TRANSMIT_RATE": DEFAULT_CONFIG.get("transmit_rate"),
            "BAUD_RATE": DEFAULT_CONFIG.get("baud_rate"),
            "L_RSSI": data['L_RSSI'],
            "R_RSSI": data['R_RSSI'],
            "L_NOISE": data['L_noise'],
            "R_NOISE": data['R_noise'],
            "PACKETS_LOST_TOTAL": 0,
            "PER": 0,
            "TEMPERATURE": data['temperature']
        }
        save_csv_row(row)
        return row
    except Exception as e:
        return {"error": str(e)}


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

        # --- Górny panel ---
        top_frame = tk.Frame(root)
        top_frame.pack(pady=10)

        ttk.Label(top_frame, text="Role:").grid(row=0, column=0, padx=5)
        ttk.Combobox(top_frame, textvariable=self.role, values=["Transmitter", "Receiver"], width=15).grid(row=0, column=1, padx=5)

        ttk.Label(top_frame, text="Test:").grid(row=0, column=2, padx=5)
        tests = ["test_1","test_2","test_3","test_4","test_5","test_6"]
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

        config_frame = tk.LabelFrame(bottom_frame, text="Current Radio Configuration")
        config_frame.grid(row=0, column=0, sticky="nsew", padx=(0,10))
        self.config_display = tk.Text(config_frame, height=20)
        self.config_display.pack(fill="both", expand=True, padx=5, pady=5)
        ttk.Button(config_frame, text="Refresh Config", command=self.refresh_config).pack(pady=5)

        stats_frame = tk.LabelFrame(bottom_frame, text="Live Statistics")
        stats_frame.grid(row=0, column=1, sticky="nsew")
        ttk.Label(stats_frame, textvariable=self.status_text, anchor="w").pack(fill="x", padx=10, pady=5)
        ttk.Label(stats_frame, textvariable=self.stats_text, anchor="w").pack(fill="x", padx=10, pady=5)

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

    def run_selected_test(self, test_name, is_receiver):
        distance = self.selected_distance.get()
        try:
            for param_set in self.test_generator(test_name):
                self.stats_text.set(f"{param_set}")
                run_test(is_receiver)
                telemetry = log_telemetry(self.port.get(), role=self.role.get())
                row = {
                    "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
                    "role": self.role.get(),
                    "test": test_name,
                    "distance_km": distance,
                    **param_set,
                    **telemetry
                }
                save_csv_row(row)
                time.sleep(0.5)
            self.status_text.set("Test finished.")
        except Exception as e:
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
                    yield {"AIR_SPEED": air_speed, "TX_RATE": transmit_rate}

        elif test_name == "test_2":
            for max_freq in TEST_2_MAX_FREQ:
                DEFAULT_CONFIG_RADIO['S9:MAX_FREQ'] = max_freq
                for transmit_rate in TEST_2_TRANSMIT_RATES:
                    if transmit_rate * 500 > DEFAULT_CONFIG["baud_rate"]/9.6:
                        continue
                    DEFAULT_CONFIG["transmit_rate"] = transmit_rate
                    yield {"MAX_FREQ": max_freq, "TX_RATE": transmit_rate}

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
                    yield {"NUM_CHANNELS": num_channels, "TX_RATE": transmit_rate}

        elif test_name == "test_5":
            for duty_cycle in TEST_5_DUTY_CYCLE:
                DEFAULT_CONFIG_RADIO['S11:DUTY_CYCLE'] = duty_cycle
                for transmit_rate in TEST_5_TRANSMIT_RATES:
                    DEFAULT_CONFIG["transmit_rate"] = transmit_rate
                    yield {"DUTY_CYCLE": duty_cycle, "TX_RATE": transmit_rate}


# ------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = MAVTestApp(root)
    root.mainloop()
