import sys, socket, threading, argparse
sys.path.append('..')
from utils import utils

"""
Example to proxy SFTP to demo.wftpserver.com on port 2222
    python3 tcp-proxy.py localhost 8080 demo.wftpserver.com 2222 true
    
Connect via:
    sftp -P 8080 localhost
    
Per https://www.wftpserver.com/onlinedemo.htm, the demo credentials are:
    Username: demo-user
    Password: demo-user
"""

def process_options():
    global listen, port, execute, command, upload_dest, target, upload
    
    parser = argparse.ArgumentParser(description='BHP TCP Proxy Tool')
    # parser.add_argument('-h', '--help', action='store_true', help='print help and exit')
    parser.add_argument('localhost', type=str, help='address on local machine to listen on')
    parser.add_argument('localport', action=utils.ConvertToInt, help='port on local machine to listen on')
    parser.add_argument('remotehost', type=str, help='address on remote machine to proxy to')
    parser.add_argument('remoteport', action=utils.ConvertToInt, help='port on remote machine to proxy to')
    parser.add_argument('receive_first', type=bool, help='receive first?')
    args = parser.parse_args()
    
    return (args.localhost, args.localport, args.remotehost, args.remoteport, args.receive_first)

def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind((local_host, local_port))
    except:
        print("[!!] Failed to listen on %s:%d" % (local_host, local_port))
        print("[!!] Check for other listening sockets or correct permissions.")
        sys.exit(0)

    print(("[*] Listening on %s:%d" % (local_host, local_port)))

    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        # print out the local connection information
        print(("[==>] Received incoming connection from %s:%d" % (addr[0], addr[1])))

        # start a thread to talk to the remote host
        proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket, remote_host, remote_port, receive_first))
        proxy_thread.start()

def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    # connect to the remote host
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))
    
    # receive data from the remote end if necessary
    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)
        
        # send it to our response handler
        remote_buffer = response_handler(remote_buffer)
        
        # if we have data to send to our local client, send it
        if len(remote_buffer):
            print(("[<==] Sending %d bytes to localhost." % len(remote_buffer)))
            client_socket.send(remote_buffer)
        
    # now lets loop and read from local... send to remote, send to local... repeat
    while True:
        # read from local host
        local_buffer = receive_from(client_socket)
        
        if len(local_buffer):
            print(("[==>] Received %d bytes from localhost." % len(local_buffer)))
            hexdump(local_buffer)
            
            # send it to our request handler
            local_buffer = request_handler(local_buffer)
            
            # send the data off to the remote host
            remote_socket.send(local_buffer)
            print("[==>] Sent to remote.")
            
        # receive the response back
        remote_buffer = receive_from(remote_socket)
        
        if len(remote_buffer):
            print(("[<==] Received %d bytes from remote." % len(remote_buffer)))
            hexdump(remote_buffer)
            
            # send to our response handler
            remote_buffer = response_handler(remote_buffer)
            
            # send the response to the local host
            client_socket.send(remote_buffer)
            
            print("[<==] Sent to localhost.")
        
        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closed connections.")
            break

# this is a pretty hex dumping function modified from the comments here:
#  http://code.activestate.com/recipes/142812-hex-dumper/
def hexdump(src, length=16):
    digits = 4 if isinstance(src, str) else 2
    for i in range(0, len(src), length):
        s = src[i:i+length]
        hexa = b' '.join([b"%0*X" % (digits, x)  for x in s])
        text = b''.join([b"%d" % (x) if 0x20 <= x < 0x7F else b'.'  for x in s])
        print( b"%04X   %-*s   %s" % (i, length*(digits + 1), hexa, text) )
    
    
def receive_from(connection):
    buffer = bytes("", 'utf8')
    
    # we set a 2 second timeout - depending on your target this may need to be
    #  adjusted accordingly
    connection.settimeout(2)
    
    try:
        # keep reading into the buffer until there's no more data or we time out
        while True:
            data = connection.recv(4096)
            
            if not data:
                break
            
            buffer += data
    except:
        pass
    
    return buffer
    
# modify any requests destined for the remote host
def request_handler(buffer):
    # perform packet modifications
    return buffer

# modify any responses destined for the local host
def response_handler(buffer):
    # perform packet modifications
    return buffer

def main():
    local_host, local_port, remote_host, remote_port, receive_first = process_options()
    
    server_loop(local_host, local_port, remote_host, remote_port, receive_first)
    
if __name__ == '__main__':
    main()
