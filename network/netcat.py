#!/usr/bin/env python3
import sys, socket, threading, subprocess, argparse
from .utils import utils
'''
Example usage:
Listening:
    ./netcat.py -l -p 9999 -c
    
Execute commands:
    ./netcat.py -t localhost -p 9999
    CTRL+D
    <BHP: #> ls -la
    ...output...
'''

# global variables
listen      = False
command     = False
upload      = False
execute     = ''
target      = ''
upload_dest = ''
port        = 0

def process_options():
    global listen, port, execute, command, upload_dest, target, upload

    parser = argparse.ArgumentParser(description='BHP Netcat Tool')
    # parser.add_argument('-h', '--help', action='store_true', help='print help and exit')
    parser.add_argument('-t', '--target', default='')
    parser.add_argument('-p', '--port', action=utils.ConvertToInt)
    parser.add_argument('-l', '--listen', action='store_true')
    parser.add_argument('-e', '--execute', default='')
    parser.add_argument('-c', '--command', action='store_true', default=False)
    parser.add_argument('-u', '--upload', default='')
    args = parser.parse_args()

    listen = args.listen
    command = args.command
    upload = args.upload or False
    execute = args.execute
    target = args.target
    upload_dest = args.upload
    port = args.port

def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # connect to our target host
        client.connect((target, port))

        if len(buffer):
            client.send(bytes(buffer, 'utf8'))

        while True:
            # now wait for data back
            recv_len = 1
            response = ''

            while recv_len:
                data = str(client.recv(4096), 'utf8')
                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break

            print(response, end = ' ')

            # wait for more input
            buffer = input('')
            buffer += '\n'

            # send it off
            client.send(bytes(buffer, 'utf8'))
    except Exception as ex:
        print('[*] Exception! Exiting...')

        # tear down the connection
        client.close()
        raise ex

def server_loop():
    global target

    # if no target is defined, we listen on all interfaces
    if not len(target):
        target = '0.0.0.0'

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))

    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        # spin off a thread to handle our new client
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()

def run_command(command):
    # trim the newline
    command = command.rstrip()

    # run the command and get the output back
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = 'Failed to execute command.\r\n'

    # send the output back to the client
    return output

def client_handler(client_socket):
    global upload, execute, command

    # check for upload
    if len(upload_dest):
        # read in all of the bytes and write to our destination
        file_buffer = ''

        # keep reading data until none is available
        while True:
            data = client_socket.recv(1024)

            if not data:
                break
            else:
                file_buffer += data

        # now we take these bytes and try to write them out
        try:
            file_desc = open(upload_dest, 'wb')
            file_desc.write(file_buffer)
            file_desc.close()

            # acknowledge that we wrote the file out
            client_socket.send(bytes('Successfully saved the file to %s\r\n' % upload_dest, 'utf8'))
        except:
            client_socket.send(bytes('Failed to save file to %s\r\n' % upload_dest, 'utf8'))

    # check for command execution
    if len(execute):
        # run the command
        output = run_command(execute)

        client_socket.send(bytes(output, 'utf8'))

    # now we go into another loop if a command shell was requested
    if command:
        while True:
            # show a simple prompt
            client_socket.send(bytes('<BHP: #> ', 'utf8'))

            # now we receive until we see a linefeed (enter key)
            cmd_buffer = ''
            while '\n' not in cmd_buffer:
                cmd_buffer += str(client_socket.recv(1024), 'utf8')

            # capture the command output
            response = run_command(cmd_buffer)

            # send back the command output
            client_socket.send(response)

def main():
    global listen, port, execute, command, upload_dest, target

    process_options()

    # determine whether this will be listening, or sending data from stdin
    if not listen and len(target) and port > 0:
        # read the buffer from the command line
        # this will block the thread, so send CTRL+D if not sending input to stdin
        buffer = sys.stdin.read()

        # send data
        client_sender(buffer)
    elif listen:
        server_loop()

if __name__ == '__main__':
    main()
