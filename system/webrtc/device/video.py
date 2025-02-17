import asyncio
import av
import aiohttp  # Librería para hacer peticiones HTTP al servidor
import cv2
import numpy as np
import time
from teleoprtc.tracks import TiciVideoStreamTrack
from cereal import messaging
from openpilot.common.realtime import DT_MDL, DT_DMON
#Adrian edit
class LiveStreamVideoStreamTrack(TiciVideoStreamTrack):
    """
    Clase que maneja la transmisión de video en vivo desde OpenPilot y lo envía tanto al socket
    como al servidor. También captura snapshots cada 200ms y los sube al servidor.
    """

    # Mapeo entre los tipos de cámara y los sockets de mensajería
    camera_to_sock_mapping = {
        "driver": "livestreamDriverEncodeData",
        "wideRoad": "livestreamWideRoadEncodeData",
        "road": "livestreamRoadEncodeData",
    }

    def __init__(self, camera_type: str):
        """
        Inicializa el stream de video y configura la conexión con el socket y el servidor.

        :param camera_type: Tipo de cámara ('driver', 'wideRoad', 'road')
        """
        dt = DT_DMON if camera_type == "driver" else DT_MDL
        super().__init__(camera_type, dt)

        # Conexión con el socket de OpenPilot para recibir datos de video en vivo
        self._sock = messaging.sub_sock(self.camera_to_sock_mapping[camera_type], conflate=True)
        self._pts = 0

        # Configuración del servidor para subir los videos y snapshots
        self.server_url = "http://195.235.211.197/videos_y_snapshots_SICUEM"  # URL del servidor de almacenamiento
        self.speed = "2.0"  # Valor de velocidad (puede cambiarse dinámicamente si se necesita)
        self.send = "1"  # Parámetro de envío al servidor

        # Configuración para snapshots (captura cada 200ms)
        self.snapshot_interval = 0.2  # 200ms
        self.last_snapshot_time = time.monotonic()  # Última vez que se guardó un snapshot

    async def send_to_server(self, packet_data):
        """
        Envía el paquete de video al servidor para su almacenamiento.

        :param packet_data: Datos del video codificados.
        """
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.server_url, data={"video": packet_data, "speed": self.speed, "send": self.send}) as response:
                    if response.status == 200:
                        print(f"[SERVER] Video data uploaded successfully for {self.camera_type}")
                    else:
                        print(f"[SERVER] Failed to upload video data for {self.camera_type}. Status: {response.status}")
            except Exception as e:
                print(f"[SERVER] Error sending video data: {e}")

    async def send_snapshot_to_server(self, image):
        """
        Convierte un frame de video en una imagen JPG y la sube al servidor cada 200ms.

        :param image: Imagen en formato NumPy (BGR).
        """
        timestamp = int(time.time() * 1000)  # Genera un timestamp en milisegundos
        filename = f"{self.camera_type}_{timestamp}.jpg"  # Nombre del archivo con el timestamp

        # Convierte la imagen a formato JPG en memoria
        _, img_encoded = cv2.imencode('.jpg', image)
        img_bytes = img_encoded.tobytes()  # Convierte la imagen a bytes para subirla al servidor

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.server_url, data={"image": img_bytes, "filename": filename, "speed": self.speed, "send": self.send}) as response:
                    if response.status == 200:
                        print(f"[SERVER] Snapshot {filename} uploaded successfully")
                    else:
                        print(f"[SERVER] Failed to upload snapshot {filename}. Status: {response.status}")
            except Exception as e:
                print(f"[SERVER] Error sending snapshot: {e}")

    async def recv(self):
        """
        Recibe los datos de video del socket de OpenPilot y los envía tanto al socket como al servidor.
        Además, cada 200ms toma un snapshot y lo envía al servidor.
        """
        while True:
            # Espera hasta recibir un mensaje de video del socket
            msg = messaging.recv_one_or_none(self._sock)
            if msg is not None:
                break
            await asyncio.sleep(0.005)  # Evita un bucle infinito consumiendo CPU

        # Extrae el contenido del mensaje
        evta = getattr(msg, msg.which())

        # Crea un paquete de video con los datos recibidos
        packet = av.Packet(evta.header + evta.data)
        packet.time_base = self._time_base  # Base de tiempo del paquete
        packet.pts = self._pts  # PTS (Presentation Time Stamp) para sincronización de video

        # Log para depuración
        self.log_debug("track sending frame %s", self._pts)

        # Incrementa el tiempo de presentación para el siguiente frame
        self._pts += self._dt * self._clock_rate

        # Sube el paquete de video al servidor en segundo plano
        asyncio.create_task(self.send_to_server(evta.header + evta.data))

        # Verifica si han pasado 200ms para capturar un snapshot
        current_time = time.monotonic()
        if current_time - self.last_snapshot_time >= self.snapshot_interval:
            # Decodifica el frame para obtener la imagen
            container = av.open(packet)
            for frame in container.decode(video=0):
                img = frame.to_ndarray(format="bgr24")  # Convierte a array NumPy en formato BGR (OpenCV)
                asyncio.create_task(self.send_snapshot_to_server(img))  # Sube la imagen en segundo plano
            self.last_snapshot_time = current_time  # Actualiza el tiempo del último snapshot

        return packet

    def codec_preference(self) -> str | None:
        """
        Especifica el códec de video preferido para la transmisión.
        """
        return "H264"
