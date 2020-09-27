from multiprocessing import cpu_count
from shutil import which


def trace_on_abort():
    from signal import signal, SIGABRT
    from traceback import format_stack


    def print_trace(_, frame):
        print(''.join(format_stack(frame)))

    signal(SIGABRT, print_trace)


print('Loading gunicorn config.')
if which('supervisord') is None:
    bind = "0.0.0.0:8000"
else:
    # bind = 'unix:/var/run/supervisor.sock'
    # bind = 'fd://0'
    bind = "0.0.0.0:8000"
worker_class = 'uvicorn.workers.UvicornWorker'
forwarded_allow_ips = "nginx"
proxy_allow_ips = "nginx"

workers = cpu_count() * 2 + 1  # TODO: WORKER TIMEOUT when preload_app = False
threads = workers  # 2-4 x $(NUM_CORES)
# timeout = 120
# graceful_timeout = 120
preload_app = True
