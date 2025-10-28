#!/usr/bin/env python3
import subprocess
import time
import random
import sys

# === CONFIG ===
SECRET = "GROK4LIFE"           # CHANGE THIS
SYMBOLS = [100, 200, 300, 400] # ms → 2 bits each
JITTER = 20                    # ±ms
INTERFACE = "wlan0"

# === ENCODE SECRET ===
def bits():
    for c in SECRET:
        b = ord(c)
        for i in range(3, -1, -1):  # 8 bits → 4 symbols
            yield (b >> (i * 2)) & 0b11

# === MAIN LOOP ===
if __name__ == "__main__":
    print(f"[AP] Encoding: {SECRET}")
    for symbol in bits():
        interval = SYMBOLS[symbol] + random.randint(-JITTER, JITTER)
        cmd = ["sudo", "iw", "dev", INTERFACE, "set", "beacon_int", str(interval)]
        subprocess.run(cmd, check=False)
        time.sleep(interval / 1000.0)  # wait for next beacon
    print("[AP] Done. Restarting in 5s...")
    time.sleep(5)
