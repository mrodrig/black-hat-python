# Usage

```bash
$ python3 rforward.py <host_to_make_available_on> -p <port_to_make_available_on> -r <traffic_destination_host>:<traffic_destination_port> --user blackhat --password
```

Example:
```bash
$ python3 rforward.py my_linux_machine -p 8080 -r my_web_server:80 --user blackhat --password
```
