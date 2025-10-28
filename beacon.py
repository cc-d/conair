#!/usr/bin/env python3
import subprocess
import time
import random
import signal
import sys

SECRET = "GROK4LIFE"           # CHANGE THIS
SYMBOLS = [100, 200, 300, 400] # Bigger gaps, no overlap
JITTER = 10                    # Tighter jitter (±10ms)
INTERFACE = "wlp6s0"
SYNC_SYMBOL = 500              # Long gap for message sync

def set_beacon_interval(ms):
    cmd = ["sudo", "iw", "dev", INTERFACE, "set", "beacon_int", str(ms)]
    subprocess.run(cmd, check=False)

def send_symbol(bits):
    interval = SYMBOLS[bits] + random.randint(-JITTER, JITTER)
    set_beacon_interval(interval)
    time.sleep(interval / 1000.0 + 0.02)  # +20ms buffer

def encode_char(c):
    b = ord(c)
    symbols = []
    for i in range(3, -1, -1):
        symbol = (b >> (i * 2)) & 0b11
        symbols.append(symbol)
    return symbols  # 4 symbols per char

def encode_secret():
    print(f"[AP] Encoding: {SECRET}")
    for c in SECRET:
        # Send sync symbol first (11 = 400ms, but longer for char start)
        set_beacon_interval(SYNC_SYMBOL)
        time.sleep(SYNC_SYMBOL / 1000.0)
        
        symbols = encode_char(c)
        for symbol in symbols:
            send_symbol(symbol)
            print(f"Sent '{c}' symbol {symbol:02b} → {SYMBOLS[symbol]}ms")
    
    # End message sync
    set_beacon_interval(100)
    print("[+] Message complete")

def signal_handler(sig, frame):
    print("\n[+] Stopping...")
    set_beacon_interval(100)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

print(f"[AP] Starting on {INTERFACE}")
set_beacon_interval(100)
time.sleep(2)

while True:
    encode_secret()
    print("[*] Repeating in 5s...")
    time.sleep(5)
