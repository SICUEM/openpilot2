
# klogger.py
from datetime import datetime
from enum import Enum
from klibs.kdate_utils import date_time_to_str
import threading
import os

# from kstopmanii.krlogclient import KRLogClient



_file_lock = threading.Lock()  # Log file lock
_socket_lock = threading.Lock()


def make_log_dir(log_dir: str):
    if not os.path.exists(log_dir):
        # Crear el directorio si no existe
        os.makedirs(log_dir)

def append_to_log_async(logstr: str, path: str, tm: datetime = datetime.now()) -> None:

    

    def append_to_file(data: str, filename: str) -> None:

        with _file_lock:  # Only one thread per turn.
            with open(filename, 'a') as file:
                if tm is None:
                    file.write(data)
                else:
                    datef = date_time_to_str(tm)
                    dataf = f'{datef} -> {data}'
                    file.write(dataf)
                file.write('\n')
                file.close()

    thread = threading.Thread(target=append_to_file, args=(logstr, path))
    thread.start()

