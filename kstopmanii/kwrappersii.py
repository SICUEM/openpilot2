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
        self._reduce_margin: int = None
        # Stop time
        self._stop_time: int = None
        # Resume speed
        self._resume_max_speed: int = None
        self._resume_accel: float = None
        self._resume_engage_speed: int = None
        # Active log channels
        self._active_log_channels: list[int] = None
        # KRServer IP
        self._krserver_ip: str = None
        self._krserver_port: str = None

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
    def reduce_margin(self) -> float:
        return self._reduce_margin

    @reduce_margin.setter
    def reduce_margin(self, value: float):
        self._reduce_margin = value

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
    def resume_accel(self) -> float:
        return self._resume_accel

    @resume_accel.setter
    def resume_accel(self, value: float):
        self._resume_accel = value

    @property
    def resume_engage_speed(self) -> int:
        return self._resume_engage_speed

    @resume_engage_speed.setter
    def resume_engage_speed(self, value: int):
        self._resume_engage_speed = value

    @property
    def active_log_channels(self) -> list("int"):
        return self._active_log_channels

    @active_log_channels.setter
    def active_log_channels(self, value: list("int")):
        self._active_log_channels = value


    @property
    def krserver_ip(self) -> str:
        return self._krserver_ip
    
    @krserver_ip.setter
    def krserver_ip(self, value) -> None:
        self._krserver_ip = value

    @property
    def krserver_port(self) -> str:
        return self._krserver_port
    
    @krserver_ip.setter
    def krserver_port(self, value) -> None:
        self._krserver_port = value

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
        self.reduce_margin = config.getint('Settings', 'reduce_margin', fallback=None)
        self.stop_time = config.getint('Settings', 'stop_time', fallback=None)
        self.resume_max_speed = config.getint('Settings', 'resume_max_speed', fallback=None)
        self.resume_accel = config.getfloat('Settings', 'resume_accel', fallback=None)
        self.resume_engage_speed = config.getint('Settings', 'resume_engage_speed', fallback=None)
        self.active_log_channels = config.get('Log', 'active_log_channels', fallback="[1,1,1]")
        self.krserver_ip = config.get('KRServer', 'rserver_ip', fallback=None)
        self.krserver_port = config.getint('KRServer', 'rserver_port', fallback=None)

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
               f"[RDM]={self.reduce_margin}km/h" \
               f"::STTM={self.stop_time}s" \
               f"::RMS={self.resume_max_speed}kph" \
               f"::RAC={self.resume_accel}m/s²" \
               f"::RES={self.resume_engage_speed}m/s²" \

    def socket_brief_i(self):
        return f"{self.in_area_dist}::" \
               f"{self.in_area_speed}::" \
               f"{self.approaching_dist}::" \
               f"{self.approaching_speed}::" \
               f"{self.stopping_dist}::" \
               f"{self.stop_dist}::" \
               f"{self.stopping_accel}::" \
               f"{self.reduce_accel}::" \
               f"{self.reduce_margin}::" \
               f"{self.stop_time}::" \
               f"{self.resume_max_speed}::" \
               f"{self.resume_accel}::" \
               f"{self.resume_engage_speed}" \

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

    #lat::long::speed::
    def socket_brief(self):
        return f'{self.lat}::{self.long}::{math.floor(self.speed * 3.6)}'

# ==== CAR CONTROL ==== #
# ==== Enums === #
class KLongControlState(Enum):
    OFF = 0
    PID = 1
    STOPPING = 2
    STARTING = 3

class KAudibleAlert(Enum):
    NONE = 0
    ENGAGE = 1
    DISENGAGE = 2
    REFUSE = 3
    WARNING_SOFT = 4
    WARNING_IMMEDIATE = 5
    PROMPT = 6
    PROMPT_REPEAT = 7
    USER_REQUESTED = 8
    DRIVER_DISTRACTED = 9

class KVisualAlert(Enum):
    NONE = 0
    FCW = 1
    STEER_REQUIRED = 2
    BRAKE_PRESSED = 3
    WRONG_GEAR = 4
    SEATBELT_UNBUCKLED = 5
    SPEED_TOO_HIGH = 6
    LDW = 7


# === Actuators === #
class KActuators:
    def __init__(self, actuators: any):
        self._actuators = actuators
        # self.gas = 0.0
        # self.brake = 0.0
        # self.steer = 0.0
        # self.steerRate = 0.0
        # self.curvature = 0.0
        # self.speed = 0.0
        # self.accel = 0.0
        # self.longControlState = KLongControlState.OFF

    @property
    def gas(self):
        return self._actuators.gas

    @property
    def brake(self):
        return self._actuators.brake

    @property
    def steer(self):
        return self._actuators.steer

    @property
    def curvature(self):
        return self._actuators.curvature

    @property
    def speed(self):
        return self._actuators.speed

    @property
    def accel(self):
        return self._actuators.accel

    @property
    def longControlState(self):
        return self._actuators.longControlState
    
    # === Brief === #
    @property
    def brief(self):
        msg = (
            f"[GAS]={self.gas}::"
            f"[BRA]={self.brake}::"
            f"[STE]={self.steer:.4f}::"
            f"[CUR]={(self.curvature * 100):.4f}::"
            f"[SPE]={self.speed}::"
            f"[ACC]={self.accel:.5f}::"
            f"[LCS]={self.longControlState}"
        )
        return msg

    @property
    def active_brief(self):
        msg = (
            f"[STE]={self.steer:.4f}::"
            f"[CUR]={(self.curvature * 100):.4f}::"
            f"[ACC]={self.accel:.5f}::"
        )
        return msg
    
# ==== Cruise ==== #
class KCruiseControl:
    def __init__(self, cruiseControl: any):
        self._cruise_ctrl = cruiseControl
        # self.cancel = False
        # self.resume = False
        # self.override = False

    # === Accesors === #
    @property
    def cancel(self):
        return self._cruise_ctrl.cancel

    @property
    def resume(self):
        return self._cruise_ctrl.resume

    @property
    def override(self):
        return self._cruise_ctrl.override

    # === Brief === #
    @property
    def brief(self):
        msg = f"[CAN]={self.cancel}::[RES]{self.resume}::[OVER]{self.override}"
        return msg


class KHudControl:
    def __init__(self, hudControl: any):
        self._hud_ctrl = hudControl
        # self.speedVisible = False
        # self.speed = 0.0
        # self.lanesVisible = False
        # self.leadVisible = False
        # self.rightLaneVisible = False
        # self.leftLaneVisible = False
        # self.rightLaneDepart = False
        # self.leftLaneDepart = False
    
    @property
    def speedVisible(self):
        return self._hud_ctrl.speedVisible

    @property
    def setSpeed(self):
        return self._hud_ctrl.setSpeed

    @property
    def lanesVisible(self):
        return self._hud_ctrl.lanesVisible

    @property
    def leadVisible(self):
        return self._hud_ctrl.leadVisible

    @property
    def rightLaneVisible(self):
        return self._hud_ctrl.rightLaneVisible

    @property
    def leftLaneVisible(self):
        return self._hud_ctrl.leftLaneVisible

    @property
    def rightLaneDepart(self):
        return self._hud_ctrl.rightLaneDepart

    @property
    def leftLaneDepart(self):
        return self._hud_ctrl.leftLaneDepart
    
    # === Brief === #
    @property
    def brief(self):
        msg = (
            f"[SPE]={self.speedVisible}::"
            f"[SET]={self.setSpeed}::"
            f"[LAN]={self.lanesVisible}::"
            f"[LEA]={self.leadVisible}::"
            f"[RIG]={self.rightLaneVisible}::"
            f"[LEF]={self.leftLaneVisible}::"
            f"[RDE]={self.rightLaneDepart}::"
            f"[LDE]={self.leftLaneDepart}"
        )
        return msg


# === KCarControl ===== #
class KCarControl:
    def __init__(self, cc: any = None):
        self._cc = cc
        self._actuators = KActuators(cc.actuators)
        self._actuators_output = KActuators(cc.actuatorsOutput)
        self._cruise_ctrl = KCruiseControl(cc.cruiseControl)
        self._hud_ctrl = KHudControl(cc.hudControl)

    # === Access to CC properties
    @property
    def enabled(self):
        return self._cc.enabled

    # Planner
    @property
    def latActive(self):
        return self._cc.latActive

    @property
    def longActive(self):
        return self._cc.longActive

    # Blinker
    @property
    def leftBlinker(self):
        return self._cc.leftBlinker

    @property
    def rightBlinker(self):
        return self._cc.rightBlinker

    # Orientation
    @property
    def orientationNED(self):
        return self._cc.orientationNED

    # Angular V
    @property
    def angularVelocity(self):

        return self._cc.angularVelocity
    
    # Actuators...
    @property
    def actuators(self):
        return self._actuators

    @property
    def actuatorsOutput(self):
        return self._actuators_output
    
    @property
    def cruiseControl(self):
        return self._cruise_ctrl
    
    @property
    def hudControl(self):
        return self._hud_ctrl

    # === Brief === #
    @property
    def brief(self):
        msg = (
            f"[ENA]={self.enabled}::"
            f"[LAT]={self.latActive}::"
            f"[LON]={self.longActive}::"
            f"[LEB]={self.leftBlinker}::"
            f"[RIB]={self.rightBlinker}::"
            f"[ORN]={self.orientationNED}::"
            f"[ANG]={self.angularVelocity}::\n"
            f"[ACT]=>{self.actuators.brief}::\n"
            f"[ACO]=>{self.actuatorsOutput.brief}::\n"
            f"[CRU]=>{self.cruiseControl.brief}::\n"
            f"[HUD]=>{self.hudControl.brief}"
        )
        return msg
    
    # === Brief === #
    @property
    def active_brief(self):
        msg = (
            f"[ENA]={self.enabled}::"
            f"[LEB]={self.leftBlinker}::"
            f"[RIB]={self.rightBlinker}::"
            f"[ACT]=>{self.actuators.active_brief}"
        )
        return msg
    
    

# ==== LATERAL PLAN ==== #
class KSolverState:
    def __init__(self, x, u):
        self._x = x
        self._u = u

    @property
    def x(self):
        return self._x

    @property
    def u(self):
        return self._u

    # === Brief === #
    def brief(self):
        # This assumes that 'x' and 'u' can be represented as strings. If they are lists or more complex objects,
        # you would need to convert them to strings in a meaningful way.
        msg = f"[X]={self.x}::[U]={self.u}"
        return msg


class KLateralPlan:
    def __init__(self, data):
        self._data = data

    @property
    def model_mono_time(self):
        return self._data.modelMonoTime

    # Add additional properties for other fields
    # ...

    @property
    def psis(self):
        return self._data.psis

    @property
    def curvatures(self):
        return self._data.curvatures

    @property
    def curvature_rates(self):
        return self._data.curvatureRates

    @property
    def solver_execution_time(self):
        return self._data.solverExecutionTime

    @property
    def solver_cost(self):
        return self._data.solverCost

    @property
    def solver_state(self):
        # Assuming self._data.solverState returns an object that has x and u attributes
        return KSolverState(self._data.solverState.x, self._data.solverState.u)

    # Enums can be represented as properties or static class variables
    Desire = {
        'none': 0,
        'turnLeft': 1,
        'turnRight': 2,
        'laneChangeLeft': 3,
        'laneChangeRight': 4,
        'keepLeft': 5,
        'keepRight': 6
    }

    LaneChangeState = {
        'off': 0,
        'preLaneChange': 1,
        'laneChangeStarting': 2,
        'laneChangeFinishing': 3
    }

    LaneChangeDirection = {
        'none': 0,
        'left': 1,
        'right': 2
    }

    @property
    def desire(self):
        return self._data.desire

    @property
    def lane_change_state(self):
        return self._data.laneChangeState

    @property
    def lane_change_direction(self):
        return self._data.laneChangeDirection

    @property
    def brief(self):
        return (f"[MOD]={self.model_mono_time}::"
                f"[DES]={self.desire}::"
                f"[LCS]={self.lane_change_state}::"
                f"[LCD]={self.lane_change_direction}::"
                f"[PSI]={self.psis}::"
                f"[CUR]={self.curvatures}::"
                f"[CRA]={self.curvature_rates}::"
                f"[SET]={self.solver_execution_time}::"
                f"[SCO]={self.solver_cost}")


# ===== CAR STATE ===== #
class KWheelV:

    def __init__(self, wheel_speed: any):
        self._whv = wheel_speed
    
    @property
    def wheel_v(self):
        return self._whv
    
    @property
    def stopped(self) -> bool:
        return self._whv.fl == 0 and self._whv.fr == 0 and self._whv.rl == 0 and self._whv.rr == 0
        

class KCarState:

    def __init__(self, cs: any) -> None:
        self._cs = cs
        self._wheels_v = KWheelV(cs.wheelSpeeds)
    
    @property
    def v_ego(self) -> float:
        return self._cs.vEgo
    
    @property
    def a_Ego(self) -> float:
        return self._cs.aEgo
    
    @property
    def gas(self) -> float:
        return self._cs.gas

    @property
    def gas_pressed(self) -> bool:
        return self._cs.gasPressed
    
    @property
    def brake(self) -> float:
        return self._cs.brake
    
    @property
    def brake_pressed(self) -> bool:
        return self._cs.brakePressed
    
    @property
    def steering_angle_deg(self) -> float:
        return self._cs.steeringAngleDeg
    
    @property
    def left_blinker(self) -> bool:
        return self._cs.leftBlinker
    
    @property
    def right_blinker(self) -> bool:
        return self._cs.rightBlinker
    
    @property
    def left_blindspot(self) -> bool:
        return self._cs.leftBlindspot
    
    @property
    def right_blindspot(self) -> bool:
        return self._cs.rightBlindspot
    
    @property
    def engine_rpm(self):
        return self._cs.engineRpm

    @property
    def stopped(self):
        return self._wheels_v.stopped

    @property
    def brief(self):
        return (f"[V]={self.v_ego}::"
                f"[A]={self.a_Ego}::"
                f"[GS]={self.gas}::"
                f"[GSP]={self.gas_pressed}::"
                f"[BRK]={self.brake}::"
                f"[BRKP]={self.brake_pressed}::"
                f"[SAD]={self.steering_angle_deg}::"
                f"[LB]={self.left_blinker}::"
                f"[RB]={self.right_blinker}::"
                f"[LBL]={self.left_blindspot}::"
                f"[RBL]={self.right_blindspot}::"
                f"[RPM]={self.engine_rpm}::"
                f"[STP]={self.stopped}")

