import socket
from datetime import datetime

from . import KLOG_SERVER_URL, KLOG_SERVER_PORT
from kstopmanii.ktimers import KTimer


MAX_DELAY = 16 # 1 minuto

class KRLogClient:

    def __init__(self, server_ip: str, server_port: int):
        self._server_ip = server_ip
        self._server_port = server_port
        self._client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._client.settimeout(None)
        self._conn = False
        self._delay = 1
        self._delay_timer = KTimer(self._delay)
        if self._server_ip is not None and self._server_port is not None:
            self._try_to_connect()
            

    def _try_to_connect(self):
        try:
            print(f"krserver: {self._server_ip}:{self._server_port}")
            self._client.connect((self._server_ip, self._server_port))
            self._conn = True
            self._delay = 0
            print(":::: CONECTED ::::::")
        except ConnectionRefusedError:
            print("KRLogServer not available")
            self._reset_socket()
        except OSError as e:
            print(f"KRLogServer conn failure :: {e.strerror}")
            self._reset_socket()
        return
    
    def inc_delay(self):
        if self._delay == 0:
            self._delay = 1
        elif self._delay * 2 <= MAX_DELAY:
            self._delay = self._delay * 2

    def send(self, data: str):
        if self._server_ip is not None and self._server_port is not None:
            if self._delay > 0:
                nw = datetime.now()
                self._delay_timer.update(nw)
            if self._delay == 0 or self._delay_timer.flag:
                try:
                    if self._conn:
                        self._client.send(data.encode("utf-8"))
                        self._delay = 0
                    else:
                        self._try_to_connect()
                except (socket.timeout, BrokenPipeError):
                    self._reset_socket()
                    print("KRLogServer -> broken pipe error")
                    print(f"=== New Delay {self._delay}")
    
    def _reset_socket(self):
        try:
            self._client.close()
            self._client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._client.settimeout(None)
            print(":::: CLOSE ::::::")
        except OSError:
            print(f"KRLogCllient: client not connected")
        
        self._conn = False
        self.inc_delay()
        self._delay_timer = KTimer(self._delay)
        print(f"=== New Delay {self._delay}")
        
        # self._client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self._client.settimeout(None)
    