#!/usr/bin/env python3
from scapy.all import *
import time
import statistics

# CONFIG
TARGET_BSSID = "58:02:05:28:3E:A7".lower() #"F4:52:46:A2:54:EC"   # ← CHANGE TO YOUR AP's BSSID
INTERFACE = "wlp2s0"
SYMBOLS = [150, 250, 350, 450]
TOLERANCE = 60                       # ±60ms = huge margin
MIN_GAP = 80                         # Ignore noise <80ms
WINDOW_SIZE = 5                      # Smooth over 5 intervals

last_time = None
intervals = []
buffer = []
decoded = ""

def classify_interval(avg_interval):
    diffs = [abs(avg_interval - s) for s in SYMBOLS]
    return diffs.index(min(diffs))

def packet_handler(pkt):
    global last_time, intervals, buffer, decoded

    if pkt.haslayer(Dot11Beacon) and pkt[Dot11].addr3 == TARGET_BSSID:
        now = time.time()
        if last_time:
            gap = (now - last_time) * 1000
            if gap > MIN_GAP:
                intervals.append(gap)
                print(f"Raw: {gap:.1f}ms", end="")

                # Smooth with moving average
                if len(intervals) > WINDOW_SIZE:
                    intervals.pop(0)
                avg = statistics.mean(intervals)
                print(f" → Avg: {avg:.1f}ms", end="")

                sym = classify_interval(avg)
                print(f" → [{sym:02b}]")

                buffer.append(sym)
                if len(buffer) == 4:
                    byte = (buffer[0]<<6) | (buffer[1]<<4) | (buffer[2]<<2) | buffer[3]
                    char = chr(byte)
                    decoded += char
                    print(f"\n[*] DECODED: {decoded}\n")
                    buffer = []
        last_time = now

print(f"[CLIENT] Sniffing {TARGET_BSSID} on {INTERFACE}...")
sniff(iface=INTERFACE, prn=packet_handler)
