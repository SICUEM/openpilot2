
# klogger.py
from datetime import datetime
from enum import Enum
from klibs.kdate_utils import date_time_to_str
import threading
import os

from kstopmanii.krlogclient import KRLogClient



_file_lock = threading.Lock()  # Log file lock
_socket_lock = threading.Lock()


def append_to_log_async(logstr: str, path: str, tm: datetime = None) -> None:

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

def rlog_async(data: str, client: KRLogClient, tm: datetime = None) -> None:
    
    def rLog() -> None:
        client.send(data)

    thread = threading.Thread(target=rLog, args=(data))
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

    def __init__(self, mode: list[KLoggerMode], log_dir: str = '/tmp/klog', krserver_ip: str = None, krserver_port: int = None):
        self._mode = mode
        self._log_dir = log_dir
        self._rlog_client = None
        self._krserver_ip = krserver_ip
        self._krserver_port = krserver_port
        if self._krserver_ip is not None and self._krserver_port is not None:
            self._rlog_client = KRLogClient(self.krserver_ip, self.krserver_port)
        if not os.path.exists(self._log_dir):
            # Crear el directorio si no existe
            os.makedirs(self._log_dir)

    # === Accesors === #
    @property
    def krserver_ip(self):
        return self._krserver_ip

    @krserver_ip.setter
    def krserver_ip(self, value):
        self._krserver_ip = value
        if self._krserver_ip is not None and self._krserver_port is not None:
            self._rlog_client = KRLogClient(self._krserver_ip, self._krserver_port)

    
    @property
    def krserver_port(self):
        return self._krserver_port

    @krserver_port.setter
    def krserver_port(self, value):
        self._krserver_port = value
        if self._krserver_ip is not None and self._krserver_port is not None:
            self._rlog_client = KRLogClient(self._krserver_ip, self._krserver_port)
    

            
    # === Ops === #
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


    def rlog(self, line: str, tm: datetime = datetime.now()):
        if KLoggerMode.IN_SOCKET in self._mode and self._krserver_ip is not None and self._krserver_port is not None:
            self._rlog_client.send(line)


