import configparser
import json
import math
import os
import shutil
import urllib
from enum import Enum
from klibs.kfile_utils import get_from_url_and_save
from . import KSETTINGS_URL, KSETTINGS_PATH, DEF_KSETTINGS_PATH, KSETTINGS_DIR
from . import KWAYPOINTS_URL, KWAYPOINTS_PATH, DEF_KWAYPOINTS_PATH, KWAYPOINTS_DIR

# ===== Params ====== #
class KStopManIIParams:
    def __init__(self):
        # Distance areas
        self._desactivation_dist = None
        self._activation_dist = None
        self._in_area_dist: int = None
        self._approaching_dist: int = None
        self._stopping_dist: int = None
        self._stop_dist: int = None
        # Cruise areas speed
        self._in_area_speed: int = None
        self._approaching_speed: int = None
        # Areas deceleration
        self._stopping_accel: float = None
        self._reduce_accel: float = None
        # Stop time
        self._stop_time: int = None
        # Resume speed
        self._resume_max_speed: int = None
        # Active log channels
        self._active_log_channels: list[int] = None

    # ==== Accesors ===== #
    @property
    def activation_dist(self) -> int:
        return self._activation_dist

    @activation_dist.setter
    def activation_dist(self, value: int):
        self._activation_dist = value

    @property
    def desactivation_dist(self) -> int:
        return self._desactivation_dist

    @desactivation_dist.setter
    def desactivation_dist(self, value: int):
        self._desactivation_dist = value

    @property
    def in_area_dist(self) -> int:
        return self._in_area_dist

    @in_area_dist.setter
    def in_area_dist(self, value: int):
        self._in_area_dist = value

    @property
    def approaching_dist(self) -> int:
        return self._approaching_dist

    @approaching_dist.setter
    def approaching_dist(self, value: int):
        self._approaching_dist = value

    @property
    def stopping_dist(self) -> int:
        return self._stopping_dist

    @stopping_dist.setter
    def stopping_dist(self, value: int):
        self._stopping_dist = value

    @property
    def stop_dist(self) -> int:
        return self._stop_dist

    @stopping_dist.setter
    def stop_dist(self, value: int):
        self._stop_dist = value

    @property
    def in_area_speed(self) -> int:
        return self._in_area_speed

    @in_area_speed.setter
    def in_area_speed(self, value: int):
        self._in_area_speed = value

    @property
    def approaching_speed(self) -> int:
        return self._approaching_speed

    @approaching_speed.setter
    def approaching_speed(self, value: int):
        self._approaching_speed = value

    @property
    def stopping_accel(self) -> float:
        return self._stopping_accel

    @stopping_accel.setter
    def stopping_accel(self, value: float):
        self._stopping_accel = value

    @property
    def reduce_accel(self) -> float:
        return self._reduce_accel

    @reduce_accel.setter
    def reduce_accel(self, value: float):
        self._reduce_accel = value

    @property
    def stop_time(self) -> int:
        return self._stop_time

    @stop_time.setter
    def stop_time(self, value: int):
        self._stop_time = value

    @property
    def resume_max_speed(self) -> int:
        return self._resume_max_speed

    @resume_max_speed.setter
    def resume_max_speed(self, value: int):
        self._resume_max_speed = value

    @property
    def active_log_channels(self) -> list("int"):
        return self._active_log_channels

    @active_log_channels.setter
    def active_log_channels(self, value: list("int")):
        self._active_log_channels = value

    # ==== Load properties ==== #
    def load_properties(self):

        def get_properties():
            try:
                # try to get and save settings
                get_from_url_and_save(KSETTINGS_URL, KSETTINGS_PATH)
                # success
                return True
            except urllib.error.HTTPError as e:
                print("Error HTTP:", e.code, e.reason)
            except urllib.error.URLError as e:
                print("Error de URL:", e.reason)
            except Exception as e:
                print("Otro error:", e)

            # if error:
            try:
                os.makedirs(KSETTINGS_DIR, exist_ok=True)
                # save default ksettings
                shutil.copy(DEF_KSETTINGS_PATH, KSETTINGS_PATH)
            except FileNotFoundError:
                current_directory = os.getcwd()
                print("El directorio de trabajo actual es:", current_directory)
                print(f"El archivo de origen {DEF_KSETTINGS_PATH} no existe")
            except PermissionError:
                print("No tiene permiso para acceder al archivo o al directorio de destino")
            except IsADirectoryError:
                print("El destino es un directorio, pero ya existe un archivo con ese nombre")
            except SameFileError:
                print("El archivo de origen y el destino son el mismo")
            except Exception as e:
                print(f"Ocurrió un error no esperado: {e}")


        # Try to put properties in properties file:
        get_properties()

        config = configparser.ConfigParser()
        config.read(KSETTINGS_PATH)
        self._activation_dist = config.getint('Settings', 'activation_dist', fallback=None)
        self._desactivation_dist = config.getint('Settings', 'desactivation_dist', fallback=None)
        self.in_area_dist = config.getint('Settings', 'in_area_dist', fallback=None)
        self.approaching_dist = config.getint('Settings', 'approaching_dist', fallback=None)
        self.stopping_dist = config.getint('Settings', 'stopping_dist', fallback=None)
        self.stop_dist = config.getint('Settings', 'stopping_dist', fallback=None)
        self.in_area_speed = config.getint('Settings', 'in_area_speed', fallback=None)
        self.approaching_speed = config.getint('Settings', 'approaching_speed', fallback=None)
        self.stopping_accel = config.getfloat('Settings', 'stopping_accel', fallback=None)
        self.reduce_accel = config.getfloat('Settings', 'reduce_accel', fallback=None)
        self.stop_time = config.getint('Settings', 'stop_time', fallback=None)
        self.resume_max_speed = config.getint('Settings', 'resume_max_speed', fallback=None)
        self.active_log_channels = config.get('Log', 'active_log_channels', fallback="[1,1,1]")

    # ==== Brief ===== #
    def brief_i(self):
        return f"IN_AR::[D]={self.in_area_dist}m:" \
               f"[S]={self.in_area_speed}kph" \
               f"::APPR::[D]={self.approaching_dist}m:" \
               f"[S]={self.approaching_speed}kph" \
               f"::STPNG::[D]={self.stopping_dist}m:" \
               f"::STP::[D]={self.stop_dist}m:" \
               f"[STPA]={self.stopping_accel}m/s²" \
               f"[RDA]={self.reduce_accel}m/s²" \
               f"::STTM={self.stop_time}s" \
               f"::RMS={self.resume_max_speed}kph"

    def socket_brief_i(self):
        return f"{self.in_area_dist}::" \
               f"{self.in_area_speed}::" \
               f"{self.approaching_dist}::" \
               f"{self.approaching_speed}::" \
               f"{self.stopping_dist}::" \
               f"{self.stop_dist}::" \
               f"{self.stopping_accel}::" \
               f"{self.reduce_accel}::" \
               f"{self.stop_time}::" \
               f"{self.resume_max_speed}"

    # ==== Debug ==== #
    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


# ===== OUTPUT ===== #
class KStopManIIOutput:
    def __init__(self):
        self._velocity: int = None
        self._acceleration: float = None
        # for test purposes...
        self._v_ego: float = None

    @property
    def velocity(self) -> int:
        return self._velocity

    @velocity.setter
    def velocity(self, value: int):
        self._velocity = value

    @property
    def acceleration(self) -> float:
        return self._acceleration

    @acceleration.setter
    def acceleration(self, value: float):
        self._acceleration = value
    # For test purposes...
    @property
    def v_ego(self) -> float:
        return self._v_ego
    
    @v_ego.setter
    def v_ego(self, value):
        self._v_ego = value
 

# ==== GPS WAY POINT ==== #

class KGPSPointType(Enum):
    UNDEFINED = "UNDF"
    STOP = "STOP"


class KGPSWayPoint:
    def __init__(self, lat: float, long: float, point_type: KGPSPointType = KGPSPointType.UNDEFINED):
        self._lat = lat
        self._long = long
        self._type = point_type

    @property
    def lat(self) -> float:
        return self._lat

    @property
    def long(self) -> float:
        return self._long

    @property
    def point_type(self) -> KGPSPointType:
        return self._type

    def brief(self) -> str:
        return f"lat={self._lat}, long={self._long}, type={self._type}"

    @classmethod
    def get_stop_waypoints(cls):
        try:
            # try to get and save settings
            get_from_url_and_save(KWAYPOINTS_URL, KWAYPOINTS_PATH)
            # success
            return True
        except urllib.error.HTTPError as e:
            print("Error HTTP:", e.code, e.reason)
        except urllib.error.URLError as e:
            print("Error de URL:", e.reason)
        except Exception as e:
            print("Otro error:", e)

        # if error:
        try:
            os.makedirs(KWAYPOINTS_DIR, exist_ok=True)
            # save default ksettings
            shutil.copy(DEF_KWAYPOINTS_PATH, KWAYPOINTS_PATH)
        except FileNotFoundError:
            current_directory = os.getcwd()
            print("El directorio de trabajo actual es:", current_directory)
            print(f"El archivo de origen {DEF_KWAYPOINTS_PATH} no existe")
        except PermissionError:
            print("No tiene permiso para acceder al archivo o al directorio de destino")
        except IsADirectoryError:
            print("El destino es un directorio, pero ya existe un archivo con ese nombre")
        except SameFileError:
            print("El archivo de origen y el destino son el mismo")
        except Exception as e:
            print(f"Ocurrió un error no esperado: {e}")

    @classmethod
    def from_json_file(cls):

        waypoints = []
        try:
            with open(KWAYPOINTS_PATH, 'r') as file:
                data = json.load(file)
                for waypoint_data in data:
                    lat = waypoint_data.get('lat')
                    long = waypoint_data.get('long')
                    ptype = waypoint_data.get('type')
                    if lat is not None and long is not None:
                        if ptype is None:
                            waypoint = cls(lat, long)
                        else:
                            waypoint = cls(lat, long, KGPSPointType(ptype))

                        waypoints.append(waypoint)
        except Exception as e:
            print(f"Error loading waypoints from file: {e}")
        return waypoints

    @staticmethod
    def calculate_end_point(start_point: any, error_gps: float, bearing: int):
        lat_rad = math.radians(start_point.lat)
        orientation_rad = math.radians(bearing)

        new_lat = start_point.lat + (error_gps / 6371.0) * (180.0 / math.pi) * math.cos(orientation_rad)
        new_lon = start_point.long + (error_gps / 6371.0) * (180.0 / math.pi) * (
                    math.sin(orientation_rad) / math.cos(lat_rad))

        return KGPSWayPoint(new_lat, new_lon)

    @staticmethod
    def calculate_path(start_point: any, error_gps: float, steps: int, bearing: int):

        if steps < 0:
            raise ValueError("steps must be > -1")
        else:
            # add start point
            path: list[KGPSWayPoint] = [start_point]
            # calculate end point:
            end_point = KGPSWayPoint.calculate_end_point(start_point, error_gps, bearing)
            if steps > 0:
                error_gps_step = error_gps / (steps + 1)
                start_coord: KGPSWayPoint = start_point
                for stp in range(steps):
                    end_coord: KGPSWayPoint = KGPSWayPoint.calculate_end_point(
                        start_coord, error_gps_step, bearing)
                    path.append(end_coord)
                    start_coord = end_coord

            # add end point
            path.append(end_point)

            return path

    @staticmethod
    def path_waypoints_brief(path: any):
        msg = ""
        for step in path:
            msg = f'{msg}{step.brief()}\n'

        return msg


# ==== GPS DATA ==== #
class KGPSLocWrapper:

    def __init__(self, gps_data: any):
        self._gps_data = gps_data

    @property
    def lat(self) -> float:
        return self._gps_data.latitude

    @property
    def long(self) -> float:
        return self._gps_data.longitude

    @property
    def speed(self) -> float:
        return self._gps_data.speed

    @speed.setter
    def speed(self, value: float):
        self._gps_data.speed = value

    def gps_error(self, other_gps_loc: KGPSWayPoint):
        def haversine_distance(lat1, long1, lat2, long2):
            R = 6371.0  # radio de la Tierra en km

            dlat = math.radians(lat2 - lat1)
            dlong = math.radians(long2 - long1)

            a = (math.sin(dlat / 2) ** 2 +
                 math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
                 math.sin(dlong / 2) ** 2)
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

            distance = R * c
            return distance

        return haversine_distance(self.lat, self.long, other_gps_loc.lat, other_gps_loc.long)

    def brief(self):
        return f'[Lt]={self.lat}::[Ln]={self.long}::[sp]={math.floor(self.speed * 3.6)}'



