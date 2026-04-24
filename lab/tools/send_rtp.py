#!/usr/bin/env python3
import socket
import struct
import sys
import time

if len(sys.argv) != 4:
    print("Usage: send_rtp.py <dst_ip> <dst_port> <packet_count>")
    sys.exit(1)

dst_ip = sys.argv[1]
dst_port = int(sys.argv[2])
packet_count = int(sys.argv[3])

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

ssrc = 0x12345678
timestamp = 0
seq = 1
payload_type = 0

for _ in range(packet_count):
    header = struct.pack("!BBHII", 0x80, payload_type, seq, timestamp, ssrc)
    payload = bytes([0xFF] * 160)
    sock.sendto(header + payload, (dst_ip, dst_port))
    seq = (seq + 1) % 65536
    timestamp += 160
    time.sleep(0.02)

print(f"Sent {packet_count} RTP packets to {dst_ip}:{dst_port}")
