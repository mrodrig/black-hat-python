import socket

target_host = "127.0.0.1"
target_port = 80

# create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# send some data
data = bytes('Hello World!', 'utf8')
client.sendto(data, (target_host, target_port))

# receive some data
data, addr = client.recvfrom(5)

print(data)
