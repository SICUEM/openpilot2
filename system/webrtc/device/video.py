import asyncio
import av
import aiohttp  # Para enviar los snapshots al servidor
import cv2
import time
import numpy as np
from teleoprtc.tracks import TiciVideoStreamTrack
from cereal import messaging
from openpilot.common.realtime import DT_MDL, DT_DMON

class LiveStreamVideoStreamTrack(TiciVideoStreamTrack):
    """
    Clase que transmite video en vivo y envía snapshots al servidor cada 200ms.
    """

    camera_to_sock_mapping = {
        "driver": "livestreamDriverEncodeData",
        "wideRoad": "livestreamWideRoadEncodeData",
        "road": "livestreamRoadEncodeData",
    }

    def __init__(self, camera_type: str):
        """
        Inicializa la conexión con el socket de video y la configuración del servidor.

        :param camera_type: Tipo de cámara ('driver', 'wideRoad', 'road')
        """
        dt = DT_DMON if camera_type == "driver" else DT_MDL
        super().__init__(camera_type, dt)

        # Conexión con el socket de OpenPilot
        self._sock = messaging.sub_sock(self.camera_to_sock_mapping[camera_type], conflate=True)
        self._pts = 0

        # Configuración del servidor para enviar snapshots
        self.server_url = "http://195.235.211.197:2204/videos_y_snapshots_SICUEM"  # Servidor de almacenamiento
        self.snapshot_interval = 0.2  # 200ms entre cada snapshot
        self.last_snapshot_time = time.monotonic()  # Última vez que se envió un snapshot

    async def send_snapshot_to_server(self, image):
        """
        Convierte un frame en una imagen JPG y la sube al servidor.

        :param image: Imagen en formato NumPy (BGR).
        """
        timestamp = int(time.time() * 1000)  # Timestamp en milisegundos
        filename = f"{self.camera_type}_{timestamp}.jpg"  # Nombre de la imagen

        # Convertir la imagen a JPG en memoria
        _, img_encoded = cv2.imencode('.jpg', image)
        img_bytes = img_encoded.tobytes()  # Convertir a bytes para subir al servidor

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.server_url, data={"image": img_bytes, "filename": filename}) as response:
                    if response.status == 200:
                        print(f"[SERVER] Snapshot {filename} uploaded successfully")
                    else:
                        print(f"[SERVER] Failed to upload snapshot {filename}. Status: {response.status}")
            except Exception as e:
                print(f"[SERVER] Error sending snapshot: {e}")

    async def recv(self):
        """
        Recibe video del socket de OpenPilot y envía snapshots cada 200ms.
        """
        while True:
            msg = messaging.recv_one_or_none(self._sock)
            if msg is not None:
                break
            await asyncio.sleep(0.005)  # Evita consumir demasiada CPU

        evta = getattr(msg, msg.which())

        # Crear un paquete de video con los datos recibidos
        packet = av.Packet(evta.header + evta.data)
        packet.time_base = self._time_base
        packet.pts = self._pts

        self.log_debug("track sending frame %s", self._pts)
        self._pts += self._dt * self._clock_rate

        # Tomar snapshot cada 200ms
        current_time = time.monotonic()
        if current_time - self.last_snapshot_time >= self.snapshot_interval:
            # Decodificar el frame para obtener imagen
            container = av.open(packet)
            for frame in container.decode(video=0):
                img = frame.to_ndarray(format="bgr24")  # Convertir a array NumPy en formato BGR (OpenCV)
                asyncio.create_task(self.send_snapshot_to_server(img))  # Subir en segundo plano
            self.last_snapshot_time = current_time  # Actualizar el tiempo del último snapshot

        return packet

    def codec_preference(self) -> str | None:
        """
        Especifica el códec de video preferido.
        """
        return "H264"
