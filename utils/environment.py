from os import getenv
from shutil import which
from socket import gethostbyname, gethostname, gaierror


def is_in_docker():
    return getenv("DOCKER", "false").upper() == "TRUE"


def is_netcat_available():
    return bool(which("nc"))


def get_current_ip():
    try:
        # gethostbyname() requires that the return value
        # of gethostname() is in /etc/hosts
        current_ip = gethostbyname(gethostname())
    except gaierror:
        # requires machine to have an internet connection
        from socket import socket, AF_INET, SOCK_DGRAM, timeout

        s = socket(AF_INET, SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
        except timeout:
            current_ip = "127.0.0.1"
        else:
            current_ip = s.getsockname()[0]
        finally:
            s.close()
    return current_ip
