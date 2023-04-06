import argparse, paramiko

def process_options():
    global listen, port, execute, command, upload_dest, target, upload
    
    parser = argparse.ArgumentParser(description='BHP TCP Proxy Tool')
    parser.add_argument('host', type=str, help='host to connect to')
    parser.add_argument('username', type=str, help='username to connect as')
    parser.add_argument('password', type=str, help='password for user')
    args = parser.parse_args()
    
    return (args.host, args.username, args.password)

def ssh_command(host, user, password, command):
    client = paramiko.SSHClient()
    # client.load_host_keys('~/.ssh/known_hosts')
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=user, password=password)
    
    ssh_session = client.get_transport().open_session()
    
    if ssh_session.active:
        ssh_session.exec_command(command)
        print((str(ssh_session.recv(1024), 'utf8')))
    
    return

if __name__ == '__main__':
    host, username, password = process_options()
    ssh_command(host, username, password, 'id')
