import socket, os

# host to listen on
host = "0.0.0.0"

# create a raw socket and bind it to the public interface
socket_protocol = socket.IPPROTO_ICMP # linux = default
if os.name == 'nt': # windows
    socket_protocol = socket.IPPROTO_IP

sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)

sniffer.bind((host, 0))

# we want the IP headers included in the capture
sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

# if we're using windows, we need to send an IOCTL to setup promiscuous mode
if os.name == 'nt':
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

# read in a single packet
print(sniffer.recvfrom(65565))

# if we're using windows, turn off promiscuous mode
if os.name == 'nt':
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
