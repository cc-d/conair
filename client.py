#!/usr/bin/env python3
from scapy.all import *
import time

# === CONFIG ===
TARGET_BSSID = "00:11:22:33:44:55"   # CHANGE: AP's MAC (see airodump-ng)
SYMBOLS = [100, 200, 300, 400]
TOLERANCE = 30
SYNC_BEACONS = 3

last_time = None
buffer = []
decoded = ""

def decode(interval):
    for i, s in enumerate(SYMBOLS):
        if abs(interval - s) <= TOLERANCE:
            return i
    return None

def packet_handler(pkt):
    global last_time, buffer, decoded
    if pkt.haslayer(Dot11Beacon) and pkt[Dot11].addr3 == TARGET_BSSID:
        now = time.time()
        if last_time:
            interval = int((now - last_time) * 1000)
            sym = decode(interval)
            if sym is not None:
                buffer.append(sym)
                print(f"[+] {interval}ms → {sym:02b}")
                if len(buffer) == 4:
                    byte = (buffer[0]<<6) | (buffer[1]<<4) | (buffer[2]<<2) | buffer[3]
                    char = chr(byte)
                    decoded += char
                    print(f"[*] DECODED: {decoded}")
                    buffer = []
        last_time = now

print(f"Sniffing for BSSID {TARGET_BSSID}...")
sniff(iface="wlan0", prn=packet_handler, timeout=120)
