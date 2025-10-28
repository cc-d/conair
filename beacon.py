#!/usr/bin/env python3
import subprocess
import time
import random
import signal
import sys

SECRET = "GROK4LIFE"           # CHANGE THIS
SYMBOLS = [150, 250, 350, 450] # ms → CLEAR GAPS
JITTER = 15                    # ±15ms max
INTERFACE = "wlp6s0"

def set_beacon_interval(ms):
    cmd = ["sudo", "iw", "dev", INTERFACE, "set", "beacon_int", str(ms)]
    subprocess.run(cmd, check=False)

def send_symbol(bits):
    interval = SYMBOLS[bits] + random.randint(-JITTER, JITTER)
    set_beacon_interval(interval)
    time.sleep(interval / 1000.0 + 0.01)  # +10ms buffer

def encode_secret():
    data = ""
    for c in SECRET:
        b = ord(c)
        for i in range(3, -1, -1):
            symbol = (b >> (i * 2)) & 0b11
            send_symbol(symbol)
            data += f"{symbol:02b}"
        print(f"Sent: '{c}' → {data[-8:]}")
    print(f"[+] Full: {SECRET}")

# Graceful exit
def signal_handler(sig, frame):
    print("\n[+] Stopping AP...")
    set_beacon_interval(100)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

print(f"[AP] Broadcasting on {INTERFACE} | Secret: {SECRET}")
set_beacon_interval(100)  # Reset
time.sleep(1)

while True:
    encode_secret()
    print("[*] Repeating in 3s...")
    time.sleep(3)
