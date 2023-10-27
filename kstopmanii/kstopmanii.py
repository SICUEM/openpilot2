
import ast
import json
from enum import Enum
import configparser
import math

from kstopmanii.kloggerii import KLoggerII, KLoggerMode, KLoggerChannel
from kstopmanii.ktimers import KTimer
from kstopmanii.kwrappersii import KGPSLocWrapper, KGPSWayPoint, KGPSPointType, KStopManIIParams, KStopManIIOutput


# ==== State ==== #
class KStopManIIState(Enum):
    RESUME = 6
    NOT_ACTIVE = 5
    DRIVING = 4
    IN_AREA = 3
    APPROACHING = 2
    STOPPING = 1
    STOPPED = 0


# ==== Log channels ==== #
class KStopManIILog(Enum):
    GPS_I_LOG = 0
    CS_I_LOG = 1
    CC_I_LOG = 2
    KPARAMS_LOG = 3
    GPS_II_LOG = 4


# ===== KStopManII ==== #
class KStopManII:
    def __init__(self):
        self._klogger: KLoggerII = KLoggerII([KLoggerMode.IN_FILE])
        self._state = None
        self._gps_points: list[KGPSWayPoint] = None
        self._next_waypoint: KGPSWayPoint = None
        self._params: KStopManIIParams = KStopManIIParams()
        self._read_params()
        self._read_gps_params()
        self._set_next_waypoint()
        self._initial_state()
        self._next_index = 0
        self._stop_timer: KTimer = None
        self._last_speed: float = 40.0
        self._activation_point: KGPSWayPoint = None

    # ==== Accesors ==== #
    @property
    def state(self):
        return self._state

    # ==== Setup state ==== #
    def _initial_state(self):
        if self._next_waypoint.point_type != KGPSPointType.UNDEFINED:
            self._state = KStopManIIState.DRIVING
            self._update_next_point()
        else:
            self._state = KStopManIIState.NOT_ACTIVE

    # ==== Params ==== #
    def _read_params(self):

        # try to read from server....


        try:
            self._params.load_properties()
            if str(KStopManIILog.KPARAMS_LOG.value) in self._params.active_log_channels:
                self._log_params()
        except FileNotFoundError:
            print(".... No params Found")

    def _log_params(self):
        params_brief = self._params.brief_i()
        print(f"{params_brief}")
        self._klogger.log_params(self._params)

    # ==== GPS Params ==== #
    def _read_gps_params(self):
        try:
            KGPSWayPoint.get_stop_waypoints()
            self._gps_points = KGPSWayPoint.from_json_file()
            if self._gps_points is not None and len(self._gps_points) > 0:
                if str(KStopManIILog.GPS_I_LOG.value) in self._params.active_log_channels:
                    self._log_gps_points()
        except FileNotFoundError:
            print("... No waypoints found")

    def _log_gps_points(self):
        gps_points = f"GPS POINTS=\n{KGPSWayPoint.path_waypoints_brief(self._gps_points)}"
        print(f"{gps_points}\n")
        self._klogger.log(gps_points, KLoggerChannel.KPARAMS_LOG)

    # ==== OPS ==== #
    def update(self, gps_data: KGPSLocWrapper):

        if self._params is not None \
                and self._gps_points is not None \
                and self._next_waypoint is not None:

            # Too far from activation point: desactive....
            if self._state == KStopManIIState.DRIVING and self._activation_point is not None:
                 act_gps_error = gps_data.gps_error(self._activation_point) * 1000
                
                 if act_gps_error > self._params.desactivation_dist:
                     self._state = KStopManIIState.NOT_ACTIVE
                     self._update_next_point()

            
            gps_error = gps_data.gps_error(self._next_waypoint)

            # Mocking speed for STOPPING state test
            spd = gps_data.speed
            if self._state == KStopManIIState.STOPPING and gps_error <= 0.005:
                spd = 0.0
                pass

            # Update state
            self._update_state(gps_error, spd)

            # Gen output
            kout = KStopManIIOutput()
            kout.velocity = self._cal_v()
            kout.acceleration = self._cal_a(kout.velocity, math.floor(gps_data.speed * 3.6))
            kout.v_ego = 1.0

            # If GPS II LOG is active, logs gps data
            self._live_log_gps_data(gps_data, gps_error, kout, self._state)

            return kout

        else:
            return None    # do nothing

    def _update_state(self, gps_error: float, speed: float):
        
        gps_error = gps_error * 1000


        if self._state == KStopManIIState.NOT_ACTIVE:
            if gps_error <= self._params.activation_dist:
                self._state = KStopManIIState.DRIVING
                self._activation_point = self._next_waypoint
                self._update_next_point()
        elif self._state == KStopManIIState.DRIVING:
            if gps_error <= self._params.in_area_dist:
                self._last_speed = math.floor(speed * 3.6)
                self._state = KStopManIIState.IN_AREA
        elif self._state == KStopManIIState.IN_AREA:
            if gps_error <= self._params.approaching_dist:
                self._state = KStopManIIState.APPROACHING
        elif self._state == KStopManIIState.APPROACHING:
            if gps_error <= self._params.stopping_dist:
                self._state = KStopManIIState.STOPPING
        elif self._state == KStopManIIState.STOPPING:
            if speed < 5:
                self._state = KStopManIIState.STOPPED
                self._stop_timer = KTimer(self._params.stop_time)
        elif self._state == KStopManIIState.STOPPED:
            self._stop_timer.update()
            if self._stop_timer.flag:
                self._update_next_point()
                self._state = KStopManIIState.RESUME
                self._stop_timer = None
        elif self._state == KStopManIIState.RESUME:
            self._state = KStopManIIState.DRIVING

    # ==== OUTPUT ==== #
    def _cal_v(self):
        speed: float = None

        if self._state == KStopManIIState.IN_AREA:
            speed = self._params.in_area_speed
        elif self._state == KStopManIIState.APPROACHING:
            speed = self._params.approaching_speed
        elif self._state == KStopManIIState.STOPPING:
            speed = 1
        elif self._state == KStopManIIState.STOPPED:
            speed = 1
        elif self._state == KStopManIIState.RESUME:
            speed = self._last_speed

        return speed

    #  speed & d_speed in k/h
    def _cal_a(self, speed, d_speed):

        accel = None
        # If Stopping or stopped:
        if self._state == KStopManIIState.STOPPING:
            accel = self._params.stopping_accel
        elif self._state == KStopManIIState.STOPPED:
            accel = self._params.stopping_accel
        # Adjust speed 
        elif speed is not None and d_speed is not None:
             if d_speed > speed:
                 accel = self._params.reduce_accel
        
        return accel

    # ==== Set destination ==== #
    def _set_next_waypoint(self):
        if len(self._gps_points) > 0:
            self._next_waypoint = self._gps_points[0]

    def _update_next_point(self):
        if self._state == KStopManIIState.NOT_ACTIVE:
            self._next_index = 0
            self._next_waypoint = self._gps_points[0]
        else:
            stop_points = [p for p in self._gps_points if p.point_type == KGPSPointType.STOP]
            self._next_waypoint = stop_points[self._next_index]
            self._next_index = self._next_index + 1
            if self._next_index >= len(stop_points):
                self._next_index = 0
        print(f"NEXT::{self._next_waypoint.lat}::{self._next_waypoint.long}")

    # ==== LOG ==== #
    def _live_log_gps_data(self, gps_data: KGPSLocWrapper, gps_error: float, kout: KStopManIIOutput, state: KStopManIIState):
        if str(KStopManIILog.GPS_II_LOG.value) in self._params.active_log_channels:
            self._log_gps_data(gps_data, gps_error, kout, state)

    def _log_gps_data(self, gps_data: KGPSLocWrapper, gps_error: float, kout: KStopManIIOutput, state: KStopManIIState):
        gps_live_data = f"[Ds]={gps_error:.{3}f}::[v]={kout.velocity}::[a]={kout.acceleration}::[st]={state}"
        print(f"{gps_data.brief()}::{gps_live_data}")
        self._klogger.log(gps_data.brief(), KLoggerChannel.GPS_I_LOG)
        self._klogger.log(gps_live_data, KLoggerChannel.GPS_II_LOG)


