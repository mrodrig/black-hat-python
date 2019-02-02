import socket, threading

bind_ip   = "0.0.0.0" # allows access outside of this host
bind_port = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind server to ip and port
server.bind((bind_ip, bind_port))

# set a max of 5 listeners
server.listen(5)

print "[*] Listening on %s:%d" % (bind_ip, bind_port)

# client-handling thread
def handle_client(client_socket):
    # print out what the client sends
    request = client_socket.recv(1024)

    print "[*] Received %s" % request

    # send data back
    client_socket.send("ACK!")

    client_socket.close()

while True:
    client, addr = server.accept()

    print "[*] Accepted connection from: %s:%d" % (addr[0], addr[1])

    # spin up our client thread to handle incoming data
    client_handler = threading.Thread(target=handle_client, args=(client,))
    client_handler.start()