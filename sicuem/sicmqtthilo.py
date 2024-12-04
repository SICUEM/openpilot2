#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import math
import time
import json
import signal
import sys
import os
from datetime import datetime
from threading import Thread, Event
from openpilot.common.params import Params
import cereal.messaging as messaging
import requests
import paho.mqtt.client as mqtt

class SicMqttHilo:

  def __init__(self):
    # Inicialización de atributos y registro de la señal SIGINT (CTRL+C)
    signal.signal(signal.SIGINT, self.signal_handler)

    self.jsonCanales = "../../sicuem/canales.json"
    self.jsonConfig = "../../sicuem/config.json"
    self.espera = 0.5
    self.indice_canal = 0
    self.conectado = False
    self.sm = None
    self.pause_event = Event()
    self.pause_event.set()
    self.stop_event = Event()  # Evento para detener hilos de manera segura
    params = Params()
    self.params = params
    self.DongleID = params.get("DongleId").decode('utf-8') if params.get("DongleId") else "DongleID"
    self.cargar_canales()



    with open(self.jsonConfig, 'r') as f:
      self.dataConfig = json.load(f)

    # Configurar el cliente MQTT
    self.mqttc = mqtt.Client()
    self.mqttc.on_connect = self.on_connect
    self.mqttc.on_disconnect = self.on_disconnect
    self.mqttc.on_message = self.on_message
    self.start_mqtt_thread()

  def start_mqtt_thread(self):
    """Inicia un hilo no bloqueante para manejar la conexión MQTT."""
    Thread(target=self.setup_mqtt_connection, daemon=True).start()

  def setup_mqtt_connection(self):
    while not self.stop_event.is_set():
      try:
        self.mqttc.connect(self.broker_address, 1883, 60)
        self.mqttc.subscribe("opmqttsender/messages", qos=0)
        self.mqttc.loop_start()
        self.conectado = True
        print("Conectado al broker MQTT con éxito.")
        break
      except Exception as e:
        print(f"Error al conectar con el broker MQTT: {e}")
        print("Reintentando conexión en 5 segundos...")
        time.sleep(5)

  def signal_handler(self, sig, frame):
    """Manejador de la señal SIGINT para detener el programa de forma controlada."""
    self.cleanup()
    sys.exit(0)

  def cleanup(self):
    """Cierra las conexiones y detiene los hilos de manera segura."""
    self.stop_event.set()  # Señal para detener los hilos
    if self.mqttc:
      self.mqttc.loop_stop()
      self.mqttc.disconnect()
    self.pause_event.set()

  def on_connect(self, client, userdata, flags, rc):
    if rc == 0:
      self.conectado = True
      print("Conectado al broker MQTT con éxito.")



  def on_disconnect(self, client, userdata, rc):
    """Maneja la desconexión del cliente MQTT y trata de reconectar."""
    self.conectado = False
    print("Desconectado del broker MQTT. Intentando reconectar...")
    self.start_mqtt_thread()

  def on_message(self, client, userdata, msg):
    """Maneja los mensajes recibidos en el tema MQTT."""
    if msg.topic == "opmqttsender/messages":
        message = msg.payload.decode()
        print(f"Mensaje recibido: {message}")
        self.params.put_bool_nonblocking("sender_uem_up", False)
        self.params.put_bool_nonblocking("sender_uem_down", False)
        self.params.put_bool_nonblocking("sender_uem_left", False)
        self.params.put_bool_nonblocking("sender_uem_right", False)
        if message == "up":
            self.params.put_bool_nonblocking("sender_uem_up", True)
        elif message == "down":
            self.params.put_bool_nonblocking("sender_uem_down", True)
        elif message == "left":
            self.params.put_bool_nonblocking("sender_uem_left", True)
        elif message == "right":
            self.params.put_bool_nonblocking("sender_uem_right", True)

  def verificar_toggle_canales(self, dataCanales):
    params = Params()
    for item in dataCanales['canales']:
      toggle_param_name = f"{item['canal']}_toggle"
      try:
        toggle_value = params.get_bool(toggle_param_name)
        if toggle_value is not None:
          nuevo_estado = 1 if toggle_value else 0
          if item['enable'] != nuevo_estado:
            self.cambiar_enable_canal(item['canal'], nuevo_estado)
      except Exception:
        pass

  def cargar_canales(self):
    """Carga la configuración de los canales desde un archivo JSON."""
    try:
      with open(self.jsonCanales, 'r') as f:
        dataCanales = json.load(f)
      self.verificar_toggle_canales(dataCanales)
      self.lista_suscripciones = [item['canal'] for item in dataCanales['canales']]
      self.enabled_items = [item for item in dataCanales['canales'] if item['enable'] == 1]
    except FileNotFoundError:
      print(f"Error: El archivo {self.jsonCanales} no existe.")
      self.lista_suscripciones = []
      self.enabled_items = []
    except json.JSONDecodeError as e:
      print(f"Error al cargar el archivo JSON {self.jsonCanales}: {e}")
      self.lista_suscripciones = []
      self.enabled_items = []

  def cambiar_enable_canal(self, canal, estado):
    with open(self.jsonCanales, 'r') as f:
      dataCanales = json.load(f)
    for item in dataCanales['canales']:
      if item['canal'] == canal:
        item['enable'] = estado
        break
    with open(self.jsonCanales, 'w') as f:
      json.dump(dataCanales, f, indent=4)
    self.cargar_canales()

  def enviar_datos_importantes(self, canal, datos):
    """Filtra y envía solo los datos importantes para el canal dado."""
    datos_importantes = {}

    if canal == 'carControl':
      keys_importantes = [
         'actuators','hudControl'
      ]

    elif canal == 'carState':
      keys_importantes = [
        'aEgo', 'cruiseState', 'leftBlinker', 'rightBlinker', 'vCruise','vCruiseCluster'
        ,'vEgo','vEgoCluster'
      ]
    elif canal == 'gpsLocationExternal':
      keys_importantes = [
        'latitude', 'longitude', 'altitude'
      ]
    elif canal == 'navInstruction':
      keys_importantes = [
        'distanceRemaining', 'maneuverDistance', 'speedLimit', 'timeRemaining'
      ]
    elif canal == 'radarState':
      keys_importantes = [
        'aRel', 'dRel', 'vRel','dRel','vLead'
      ]
    elif canal == 'drivingModelData':
      keys_importantes = [
        'laneLineMeta'
      ]
    # Añade más condicionales según los datos relevantes de otros canales si es necesario

    for key in keys_importantes:
      if key in datos:
        datos_importantes[key] = datos[key]

    return datos_importantes

  def pausar_envio(self):
    self.pause_event.clear()
    self.dataConfig['config']['send']['value'] = 0

  def reanudar_envio(self):
    self.pause_event.set()
    self.dataConfig['config']['send']['value'] = 1

  def conexion(self, url='http://www.google.com', intervalo=5):
    """Verifica la conexión a Internet periódicamente en un hilo separado."""
    def check_connection():
      while not self.stop_event.is_set():
        try:
          response = requests.get(url, timeout=5)
          if response.status_code == 200:
            print("Conexión a Internet exitosa.")
        except requests.ConnectionError:
          print(f"No hay conexión a Internet. Intentando nuevamente en {intervalo} segundos...")
        time.sleep(intervalo)
    Thread(target=check_connection, daemon=True).start()

  def obtener_gps_location(self):
    # Crear una instancia del SubMaster para obtener datos del canal 'gpsLocationExternal'
    sm = self.sm

    # Actualizar para obtener los datos más recientes
    sm.update(0)

    # Verificar si el mensaje de gpsLocationExternal es válido
    try:
      self.sm.update(0)
      latitude = sm['gpsLocationExternal'].latitude
      longitude = sm['gpsLocationExternal'].longitude
      altitude = sm['gpsLocationExternal'].altitude
    except KeyError as e:
      print(f"Error: Canal no disponible - {e}")
      latitude, longitude, altitude = None, None, None

    return {
      "latitude": latitude,
      "longitude": longitude,
      "altitude": altitude
    }



  def haversine_distance(self,lat1, lon1, lat2, lon2):
    # Radio de la Tierra en metros
    R = 6371000
    # Convertir coordenadas de grados a radianes
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    # Calcular la distancia usando la fórmula haversine
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

  def ponerAMenos1distancia(self):
    self.params.put("roundabout_distance",
                    "-1")
    self.params.put("intersection_distance",
                    "-1")
    self.params.put("merge_distance",
                    "-1")

  def enviar_estado_archivo_mapbox(self):
    # Obtener la posición GPS actual desde el canal 'gpsLocationExternal'
    gps_data = self.obtener_gps_location()
    current_lat = gps_data.get('latitude')
    current_lon = gps_data.get('longitude')
    #print(current_lat)
    #print(current_lon)
    self.ponerAMenos1distancia()

    ruta_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_archivo = os.path.join(ruta_actual, "../system/manager/mapbox_response.json")

    if os.path.exists(ruta_archivo):

      try:
        with open(ruta_archivo, 'r') as archivo:
          data = json.load(archivo)
          closest_maneuvers = {
            "roundabout": {"distance": float('inf'), "latitude": None, "longitude": None},
            "intersection": {"distance": float('inf'), "latitude": None, "longitude": None},
            "merge": {"distance": float('inf'), "latitude": None, "longitude": None}
          }

          # Analizar las rutas y encontrar maniobras específicas
          if "routes" in data and len(data["routes"]) > 0:
            for leg in data["routes"][0].get("legs", []):
              for step in leg.get("steps", []):
                maneuver_type = step.get("maneuver", {}).get("type", "")
                distance = step.get("distance", 0)
                maneuver_lat = step.get("maneuver", {}).get("location", [None, None])[1]
                maneuver_lon = step.get("maneuver", {}).get("location", [None, None])[0]

                if maneuver_type in closest_maneuvers:
                  # Calcular la distancia manualmente si las coordenadas son válidas
                  if current_lat is not None and current_lon is not None and maneuver_lat is not None and maneuver_lon is not None:
                    # Conversión de coordenadas a radianes
                    lat1 = current_lat * (3.141592653589793 / 180)
                    lon1 = current_lon * (3.141592653589793 / 180)
                    lat2 = maneuver_lat * (3.141592653589793 / 180)
                    lon2 = maneuver_lon * (3.141592653589793 / 180)

                    # Fórmula de Haversine
                    dlat = lat2 - lat1
                    dlon = lon2 - lon1
                    a = (math.sin(dlat / 2) ** 2 +
                         math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2)
                    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
                    R = 6371000  # Radio de la Tierra en metros
                    calculated_distance = R * c

                    # Actualizar la distancia si es más cercana

                    closest_maneuvers[maneuver_type]["distance"] = calculated_distance
                    closest_maneuvers[maneuver_type]["latitude"] = maneuver_lat
                    closest_maneuvers[maneuver_type]["longitude"] = maneuver_lon
                    #print(calculated_distance)


          # Establecer las distancias en Params, enviando -1 si no se encuentra ninguna maniobra
          self.params.put("roundabout_distance",
                          str(closest_maneuvers["roundabout"]["distance"]) if closest_maneuvers["roundabout"][
                                                                                "distance"] != float('inf') else "-1")
          self.params.put("intersection_distance",
                          str(closest_maneuvers["intersection"]["distance"]) if closest_maneuvers["intersection"][
                                                                                  "distance"] != float('inf') else "-1")
          self.params.put("merge_distance",
                          str(closest_maneuvers["merge"]["distance"]) if closest_maneuvers["merge"][
                                                                           "distance"] != float('inf') else "-1")

          # Preparar el contenido para MQTT
          contenido = (
            f"Roundabout distance: {self.params.get('roundabout_distance').decode('utf-8')} m\n"
            f"Intersection distance: {self.params.get('intersection_distance').decode('utf-8')} m\n"
            f"Merge distance: {self.params.get('merge_distance').decode('utf-8')} m"
          )
          if not self.params.get_bool("mapbox_toggle"):
            print("mapbox desactivado")
          else:
            #print("envia mapbox distancia")
            self.mqttc.publish("telemetry_mqtt/mapbox_status", contenido, qos=0)
      except Exception as e:
        print(f"Error al leer el archivo: {e}")
    else:
      pass

  def loop(self):
    self.conexion()
    hilo_ping = Thread(target=self.loopPing, daemon=True)
    hilo_ping.start()
    while not self.stop_event.is_set():
      self.pause_event.wait()
      self.cargar_canales()
      if len(self.enabled_items) > 0 and self.sm:
        for canal_actual in self.enabled_items:
          canal_nombre = canal_actual['canal']
          if canal_nombre in self.sm.data:
            try:
              self.sm.update()
              # Convierte los datos de SubMaster a un diccionario
              datos_canal = self.sm[canal_nombre].to_dict()
              # Envía solo los datos importantes
              datos_importantes = self.enviar_datos_importantes(canal_nombre, datos_canal)
              self.mqttc.publish(
                str(canal_actual['topic']).format(self.DongleID),
                json.dumps(datos_importantes),
                qos=0
              )
            except KeyError:
              continue


      ruta_actual = os.path.dirname(os.path.abspath(__file__))
      ruta_archivo = os.path.join(ruta_actual, "../system/manager/mapbox_response.json")
      if os.path.exists(ruta_archivo):
       self.enviar_estado_archivo_mapbox()
      time.sleep(self.espera)

  def loopPing(self):
    """Bucle que publica mensajes de ping periódicamente sin bloquear."""
    while not self.stop_event.is_set():
      self.pause_event.wait()
      self.mqttc.publish("telemetry_config/ping", str(time.time()), qos=0)
      time.sleep(3)

  def start(self) -> int:
    self.cargar_canales()
    if self.lista_suscripciones:
      try:
        self.sm = messaging.SubMaster(['carState', 'controlsState', 'liveCalibration', 'carControl', 'gpsLocationExternal','gpsLocation','navInstruction','radarState','drivingModelData'])
      except Exception:
        self.sm = None
    time.sleep(2)
    hilo_telemetry = Thread(target=self.loop, daemon=True)
    hilo_telemetry.start()
    return 0

if __name__ == "__main__":
    sic_mqtt_hilo = SicMqttHilo()
    sic_mqtt_hilo.start()
