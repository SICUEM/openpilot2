
# klogger.py
from datetime import datetime
from enum import Enum
from klibs.kdate_utils import date_time_to_str
import threading
import os


_file_lock = threading.Lock()  # Log file lock


def append_to_log_async(logstr: str, path: str, tm: datetime = None) -> None:
    """
    Append a string to the end of a text file asynchronously.
    Synchronize access to the file to prevent write conflicts.

    Args:
        logstr (str): log string.
        path (str): file path.
        :param tm: timestamp
    """

    def append_to_file(data: str, filename: str) -> None:
        """
        Función auxiliar para escribir datos en un archivo.
        """

        with _file_lock:  # Only one thread per turn.
            with open(filename, 'a') as file:
                if tm is None:
                    file.write(data)
                else:
                    datef = date_time_to_str(tm)
                    dataf = f'{datef} -> {data}'
                    file.write(dataf)
                file.write('\n')  # Agregar un salto de línea después de cada entrada.
                file.close()

    # Creamos y arrancamos un nuevo hilo para la operación de escritura.
    thread = threading.Thread(target=append_to_file, args=(logstr, path))
    thread.start()


class KLoggerMode(Enum):
    IN_SOCKET = 1
    IN_FILE = 0


class KLoggerChannel(Enum):
    GENR_I_LOG = "k.generic_i.log"
    GPS_I_LOG = "k.gps_i.log"
    CS_I_LOG = "k.cs_i.log"
    CC_I_LOG = "k.cc_i.log"
    KPARAMS_LOG = "k.kparams.log"
    GPS_II_LOG = "k.gps_ii.log"


class KLoggerII:

    def __init__(self, mode: list[KLoggerMode], log_dir: str = '/tmp/klog'):
        self._mode = mode
        self._log_dir = log_dir
        if not os.path.exists(self._log_dir):
            # Crear el directorio si no existe
            os.makedirs(self._log_dir)

    def log(self, line: str, channel: KLoggerChannel = KLoggerChannel.GENR_I_LOG, tm: datetime = datetime.now()):
        if KLoggerMode.IN_FILE in self._mode:
            append_to_log_async(line, f'{self._log_dir}/{channel.value}', tm)

    def log_params(self, params: any, tm: datetime = datetime.now()):
        chan = KLoggerChannel.KPARAMS_LOG
        if KLoggerMode.IN_FILE in self._mode:
            line = params.brief_i()
            append_to_log_async(line, f'{self._log_dir}/{chan.value}', tm)
        if KLoggerMode.IN_SOCKET in self._mode:
            line = params.socket_brief_i()
            # TODO: Change for socket
            append_to_log_async(line, f'{self._log_dir}/{chan.value}', tm)






