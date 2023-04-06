# Demo Files
This uses demo files from the Paramiko project. These files were obtained from:
https://github.com/paramiko/paramiko/tree/master/demos

# Running

## Server

The system that you want to be able to enter commands on, but will not run the commands itself, use:
```bash
$ python3 ssh-server.py localhost 22
```

This will allow the SSH client to connect to it. The SSH client will then receive commands, 
execute them, and send the output back to the server where it will be printed out.

## Client
```bash
$ python3 ssh-receive-command.py localhost 22 blackhat python
```
