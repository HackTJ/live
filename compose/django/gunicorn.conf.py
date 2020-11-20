from os import environ
from multiprocessing import cpu_count
from shutil import which
from os.path import exists


print('Loading gunicorn config.')


def trace_on_abort():
    from signal import signal, SIGABRT
    from traceback import format_stack

    def print_trace(_, frame):
        print(''.join(format_stack(frame)))

    signal(SIGABRT, print_trace)


port = environ.get('PORT', 8000)
if which('supervisord') is None:
    bind = f"0.0.0.0:{port}"
else:
    # bind = 'unix:/var/run/supervisor.sock'
    # bind = 'fd://0'
    bind = f"0.0.0.0:{port}"
worker_class = 'uvicorn.workers.UvicornWorker'
forwarded_allow_ips = "nginx"
proxy_allow_ips = "nginx"

workers = cpu_count() * 2 + 1  # TODO: WORKER TIMEOUT when preload_app = False
threads = workers  # 2-4 x $(NUM_CORES)
# timeout = 120
# graceful_timeout = 120
preload_app = True

if exists('/dev/shm'):
    worker_tmp_dir = '/dev/shm'
else:
    # if we try to set worker_tmp_dir to /dev/shm, we get:
    # RuntimeError: /dev/shm doesn't exist. Can't create workertmp.
    pass  # go with the default
