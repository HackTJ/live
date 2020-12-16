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

        google_test_socket = socket(AF_INET, SOCK_DGRAM)
        try:
            google_test_socket.connect(("8.8.8.8", 80))
        except timeout:
            current_ip = "127.0.0.1"
        else:
            current_ip = google_test_socket.getsockname()[0]
        finally:
            google_test_socket.close()
    return current_ip


def pg_isready(dbname=None, host=None, port=None, username=None):
    if which("pg_isready"):
        from subprocess import run

        p = run(
            [
                "pg_isready",
                f"--dbname={dbname}" if dbname else "",
                f"--host={host}" if host else "",
                f"--port={port}" if port else "",
                f"--username={username}" if username else "",
            ]
        )
        if p.returncode == 0:
            return True
        elif p.returncode == 1:
            return False
        elif p.returncode == 2:
            # TODO: maybe don't raise a psycopg2 error? raising a dependency's
            # error might be confusing.
            # from psycopg2 import OperationalError
            #
            # raise OperationalError("There was no response to the connection attempt.")

            return False
        elif p.returncode == 3:
            # TODO: maybe don't raise a psycopg2 error? raising a dependency's
            # error might be confusing.
            from psycopg2 import ProgrammingError

            raise ProgrammingError(
                "No attempt to call the pg_isready command was "
                "made, perhaps due to invalid parameters."
            )
        else:
            raise ValueError("Received an unexpected return code from pg_isready.")
    else:
        from psycopg2 import connect as connect_db, OperationalError

        kwargs = {}
        if dbname:
            kwargs["dbname"] = dbname  # TODO: different format from command
            kwargs["user"] = username
            # kwargs['password'] = password
            kwargs["host"] = host
            kwargs["port"] = port
        try:
            connect_db(**kwargs).close()
        except OperationalError:
            return False
        else:
            return True
