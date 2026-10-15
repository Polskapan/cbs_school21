#!/usr/bin/env python3
from scapy.all import IP, TCP, Raw, send, wrpcap

packet = IP(dst="127.0.0.1")/TCP(dport=12345, flags="PA", seq=1000, ack=0)/Raw(load="Dear Steel Cat! This is no attack, it's my humster Pinkie you should track")
send(packet, verbose=0)
print("packet send")
wrpcap("sent_message.pcapng", packet)
print("pcapng file created")
