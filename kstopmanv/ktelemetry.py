from datetime import datetime
import socket
import time
import threading
from queue import Queue

from kstopmanii.ktimers import KTimer

from . import TELEM_SRV_IP, TELEM_SRV_PORT, TELEM_ACTIVE, TELEM_CONN_DELAY, TELEM_FREQ


class KTelemetry:
    # === C === #
    def __init__(self) -> None:
        self._tlm_srv_ip = None
        self._tlm_srv_port = None
        self._tlm_active = False
        self._tlm_conn_delay = 1
        self._tlm_up_freq = 10
        self._read_config()

        self._msg_q = Queue()
        self._tlm_timer = KTimer(self._tlm_up_freq)

        self._tlm_thread = threading.Thread(
            target=self._tcp_client_thread, 
            args=(self._tlm_srv_ip, self._tlm_srv_port, 
                  self._tlm_conn_delay, self._msg_q))
        self._tlm_thread.start()

    # === Setup === #
    def _read_config(self):
        # TODO: Try to read form URL
        self._tlm_srv_ip = TELEM_SRV_IP
        self._tlm_srv_port = TELEM_SRV_PORT
        self._tlm_active = TELEM_ACTIVE
        self._tlm_conn_delay = TELEM_CONN_DELAY
        self._tlm_up_freq = TELEM_FREQ

    # === Ops === #
    def log(self, msg):
        self._msg_q.put(msg)
    
    # === Client Thread === #
    def _tcp_client_thread(self, server_ip, server_port, conn_delay, msg_q: Queue):
        while True:
            try:
                # Intentar conectar con el servidor
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.connect((server_ip, int(server_port)))
                    print("TELEMETRY OK ============ :)")
                    while True:
                        nw = datetime.now()
                        self._tlm_timer.update(nw)
                        if self._tlm_timer.flag and not msg_q.empty():
                            # msg_q.join()
                            msg = f""
                            while not msg_q.empty():
                                msg = f"{msg}{msg_q.get()}"
                            sock.sendall(msg.encode())
                        time.sleep(1)  # Esperar antes de enviar otro mensaje

            except ConnectionError as e:
                print("TELEMETRY KO ================")
                #print(f"Error: {e}")
                #print(f"Reintentando en {conn_delay} segundos...")
                time.sleep(conn_delay)

