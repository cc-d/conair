#!/usr/bin/env python3
from scapy.all import *
import time
import statistics

TARGET_BSSID = "F4:52:46:A2:54:EC"  # Your AP BSSID
INTERFACE = "wlp2s0mon"             # Monitor interface
SYMBOLS = [100, 200, 300, 400]
SYNC_SYMBOL = 500
TOLERANCE = 40                      # ±40ms (tight but safe)
MIN_GAP = 50                        # Ignore tiny gaps
CHAR_BUFFER = []                    # Collects 4 symbols per char
MESSAGE_BUFFER = ""                 # Full decoded message

last_time = None
char_count = 0

def decode_symbol(gap):
    # Direct classification — NO averaging!
    diffs = [abs(gap - s) for s in SYMBOLS]
    min_diff = min(diffs)
    if min_diff <= TOLERANCE:
        return diffs.index(min_diff)
    elif abs(gap - SYNC_SYMBOL) <= 80:  # Sync gap
        return -1  # Sync marker
    return None  # Invalid

def packet_handler(pkt):
    global last_time, CHAR_BUFFER, MESSAGE_BUFFER, char_count
    
    if pkt.haslayer(Dot11Beacon) and pkt[Dot11].addr3 == TARGET_BSSID:
        now = time.time()
        if last_time:
            gap = int((now - last_time) * 1000)
            if gap >= MIN_GAP:
                sym = decode_symbol(gap)
                if sym is not None:
                    if sym == -1:
                        # Sync: start new char
                        if len(CHAR_BUFFER) == 4:
                            # Process previous char
                            byte = sum(s << (6 - i*2) for i, s in enumerate(CHAR_BUFFER))
                            char = chr(byte)
                            MESSAGE_BUFFER += char
                            print(f"\n[*] Char {char_count}: '{char}' | Full: {MESSAGE_BUFFER}")
                            char_count += 1
                        CHAR_BUFFER = []
                        print(f"[SYNC] New char starting...")
                    else:
                        # Data symbol
                        CHAR_BUFFER.append(sym)
                        print(f"[+] Gap: {gap}ms → {sym:02b} | Buffer: {CHAR_BUFFER}")
                        
                        # Auto-process if 4 symbols (no need for sync end)
                        if len(CHAR_BUFFER) == 4:
                            byte = sum(s << (6 - i*2) for i, s in enumerate(CHAR_BUFFER))
                            char = chr(byte)
                            MESSAGE_BUFFER += char
                            print(f"\n[*] Char {char_count}: '{char}' | Full: {MESSAGE_BUFFER}")
                            char_count += 1
                            CHAR_BUFFER = []
                else:
                    print(f"[?] Invalid gap: {gap}ms (ignored)")
        last_time = now

print(f"[CLIENT] Sniffing {TARGET_BSSID} on {INTERFACE}...")
sniff(iface=INTERFACE, prn=packet_handler)
