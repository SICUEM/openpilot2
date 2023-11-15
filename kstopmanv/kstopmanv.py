from datetime import datetime
import math
from kstopmanii.kloggerii import append_to_log_async
from kstopmanii.ktimers import KTimer
from . import CRUISE_CONTROL, CRUISE_V_MIN, IN_AREA_D, APPROACHING_D, \
STOPPING_D, STOP_T, RESUME_D, IN_AREA_V, APPROACHING_V, \
RESUME_V, RESUME_A, STOP_V_THRES, STOP_POINTS, ACTIVATION_D



# ==== KSTOPMAN V ==== #
# noinspection PyMethodMayBeStatic
class KStopManV:
    # ==== State ==== #
    class State:
        DEACTIVATED = "OFF"
        STOPPED = "STP"
        RESUME = "RES"
        DRIVING = "DRI"
        IN_AREA = "IN_A"
        APPROACHING = "APPR"
        STOPPING = "STPG"

    # ==== Params ==== #
    class Params:
        # == Params C == #
        def __init__(self):
            self._d_activation = None   # activation d (m)
            self._v_cru_lim = None      # cruise v min (kph)
            self._v_appro_st = None     # approach v
            self._v_in_area_st = None   # in area v
            self._0_threshold_v = None  # 0 threshold (kph)
            self._v_resume = None  # resume target v (kph)
            self._a_resume = None  # resume accel (m/s²)

            self._r_appro_st = None  # approaching distance (m)
            self._r_in_area_st = None  # in area distance (m)
            self._r_stopping_st = None  # stopping distance (m)
            self._t_stop = None  # stop time (s)

            self._cruise_ctrl = True     # cruise control active

            self.read()     # Read params

        # == Read == #
        def read(self):
            # TODO: Read from URL
            # TODO: Read from file

            # For test purposes
            self._d_activation = ACTIVATION_D
            self._v_cru_lim = CRUISE_V_MIN
            self._r_in_area_st = IN_AREA_D
            self._r_appro_st = APPROACHING_D
            self._r_stopping_st = STOPPING_D
            self._t_stop = STOP_T

            self._v_in_area_st = IN_AREA_V
            self._v_appro_st = APPROACHING_V
            self._0_threshold_v = STOP_V_THRES
            self._v_resume = RESUME_V
            self._a_resume = RESUME_A

            self._cruise_ctrl = CRUISE_CONTROL

        # == Accesors == #
        @property
        def activation_d(self):
            return self._d_activation

        @property
        def cruise_v_limit(self):
            return self._v_cru_lim

        @property
        def approaching_v(self):
            return self._v_appro_st

        @property
        def in_area_v(self):
            return self._v_in_area_st

        @property
        def zero_threshold_v(self):
            return self._0_threshold_v

        @property
        def resume_v(self):
            return self._v_resume
        
        @property
        def resume_a(self):
            return self._a_resume

        @property
        def approaching_d(self):
            return self._r_appro_st

        @property
        def in_area_d(self):
            return self._r_in_area_st

        @property
        def stopping_d(self):
            return self._r_stopping_st

        @property
        def stop_t(self):
            return self._t_stop

        @property
        def cruise_ctrl(self):
            return self._cruise_ctrl

        # === Map === #
        def __str__(self):
            return (
                f"Params("
                f"cruise_v_limit={self.cruise_v_limit}, "
                f"approaching_v={self.approaching_v}, "
                f"in_area_v={self.in_area_v}, "
                f"zero_threshold_v={self.zero_threshold_v}, "
                f"resume_v={self.resume_v}, "
                f"resume_a={self.resume_a}, "
                f"approaching_d={self.approaching_d}, "
                f"in_area_d={self.in_area_d}, "
                f"stopping_d={self.stopping_d}, "
                f"stop_t={self.stop_t})"
            )

    # ==== Update params ==== #
    class UpdateParams:
        def __init__(self, gps_data: any, cs: any, d_traveled: int):
            self._gps_data = gps_data
            self._cs = cs
            self._d_traveled = d_traveled

        @property
        def lat(self):
            return self._gps_data.latitude

        @property
        def lon(self):
            return self._gps_data.lon

        @property
        def d_traveled_m(self):
            return self._d_traveled

        @property
        def d_traveled_km(self):
            return self._d_traveled
        

        @property
        def v_0(self):
            wh_v = self._cs.wheelSpeeds
            return wh_v.fl == 0 and wh_v.fr == 0 and wh_v.rl == 0 and wh_v.rr == 0

        @property
        def v_kph(self):
            return self._gps_data.speed * 3.6
        
        @property
        def v_ms(self):
            return self._gps_data.speed

    # == KStopManV C == #
    def __init__(self):
        self._params = self.Params()            # Read params
        self._st_current_d = 0                  # State distance traveled
        self._state = self.State.DEACTIVATED    # current state
        self._cruise_v_out = None               # cruise v (output)
        self._v_out = None                          # v (output)
        self._a_out = None                          # a (output)
        self._d_trvl = 0

        self._last_state = None                 #
        self._st_changed = False             #
        self._st_traveled_d = 0
        self._st_ini_d = 0
        self._st_ini_v = 0
        self._st_stop_d = 0

        self._stop_pts = STOP_POINTS
        self._stop_pt_idx = 0
        self._end_flag = False

        self._stop_timer: KTimer = None

        self._v_0: bool = True

        # TODO: Remove this member:
        # self._d_trv = None                      # distance traveled

    # == Accesors == #
    @property
    def cruise_v(self) -> int:
        return self._cruise_v_out

    @property
    def v_ms(self) -> float:
        if self._v_out is not None:
            return self._v_out / 3.6
        else:
            return self._v_out

    @property
    def v_kph(self) -> float:
        return self._v_out

    @property
    def a_ms(self) -> float:
        return self._a_out

    @property
    def state(self) -> str:
        return self._state

    @property
    def d_trvl(self) -> int:
        return self._d_trvl

    @property
    def v_0(self) -> bool:
        return self._v_0

    # == OPs == #
    def update(self, u_params: UpdateParams):
        self._set_u_params(u_params)
        self._update_state(u_params)
        self._reset_state(u_params)
        if self._params.cruise_ctrl:
            self._update_cruise()
        self._update_v(u_params)
        self._update_a(u_params)
    
    def _set_u_params(self, u_params: UpdateParams):
        self._d_trvl = u_params.d_traveled_m

    def _reset_state(self, u_params: UpdateParams):
        if self._st_changed:
            self._st_traveled_d = 0
            self._st_ini_d = u_params.d_traveled_m
            self._st_ini_v = u_params.v_kph
            if not self._end_flag:
                self._st_stop_d = self._d_nxt_stop(u_params.d_traveled_m)

    def _update_state(self, up_params: UpdateParams):
        # TODO: Fix state transitions:
        self._last_state = self._state      # save last state
        self._st_changed = False         # state changed flag
        self._v_0 = up_params.v_0       # v = 0 ??
        d_trv = up_params.d_traveled_m           # get distance traveled
        if not self._end_flag:
            d_nxt_stop = self._d_nxt_stop(d_trv)     # distance to nex stop

        if self._state == self.State.DEACTIVATED:
            if d_trv > self._params.activation_d and not self._end_flag:
                self._state = self.State.DRIVING
        elif self._state == self.State.DRIVING:
            if d_nxt_stop < self._params.in_area_d:
                self._state = self.State.IN_AREA
        elif self._state == self.State.IN_AREA:
            if d_nxt_stop < self._params.approaching_d:
                self._state = self.State.APPROACHING
        elif self._state == self.State.APPROACHING:
            if d_nxt_stop < self._params.stopping_d:
                self._state = self.State.STOPPING
        elif self._state == self.State.STOPPING:
            if self._v_0:
                self._state = self.State.STOPPED
                self._stop_pt_idx = self._stop_pt_idx + 1
                self._stop_timer = KTimer(self._params.stop_t)
                if self._stop_pt_idx >= len(self._stop_pts):
                    self._end_flag = True
        elif self._state == self.State.STOPPED:
            now = datetime.now()
            self._stop_timer.update(now)
            if self._stop_timer.flag:
                self._state = self.State.RESUME
        elif self._state == self.State.RESUME:
            if up_params.v_kph >= self._params.resume_v:
                if not self._end_flag:
                    self._state = self.State.DRIVING
                else:
                    self._state = self.State.DEACTIVATED

        self._st_changed = self._last_state != self._state

    def _update_cruise(self):
        self._cruise_v_out = None
        if self._st_changed:
            if self._state == self.State.IN_AREA:
                self._cruise_v_out = self._params.in_area_v
            elif self._state == self.State.APPROACHING:
                self._cruise_v_out = self._params.approaching_v
            elif self._state == self.State.STOPPING:
                self._cruise_v_out = 0
            elif self._state == self.State.RESUME:
                self._cruise_v_out = self._params.cruise_v_limit

        if self._cruise_v_out is not None \
                and self._cruise_v_out < self._params.cruise_v_limit:
            self._cruise_v_out = self._params.cruise_v_limit

    def _update_v(self, params: UpdateParams):

        def calc_v(current_d: int, init_v: float, final_v: float, fin_d: int):
            current_d = math.floor(current_d)
            init_v = math.floor(init_v)
            final_v = math.floor(final_v)
            fin_d = math.floor(fin_d)
            slope = (final_v - init_v) / fin_d
            current_v = slope * current_d + init_v
            # msg = f"currentD:{current_d}\tiniV:{init_v}\tfinalV:{final_v}\tcurrentV:{current_v}\tfinalD:{fin_d}\tgpsV:{params.v_ms}"
            # append_to_log_async(msg, "/tmp/klog/k.calc_v", datetime.now())
            return current_v

        self._v_out = None

        if self._state == self.State.IN_AREA:
            # state d traveled
            self._st_traveled_d = params.d_traveled_m - self._st_ini_d
            final_d = self._params.in_area_d - self._params.approaching_d
            self._v_out = calc_v(
                self._st_traveled_d,
                self._st_ini_v,
                self._params.in_area_v,
                final_d
            )
        elif self._state == self.State.APPROACHING:
            # state d traveled
            self._st_traveled_d = params.d_traveled_m - self._st_ini_d
            final_d = self._params.approaching_d - self._params.stopping_d
            self._v_out = calc_v(
                self._st_traveled_d,
                self._st_ini_v,
                self._params.approaching_v,
                final_d
            )
        elif self._state == self.State.STOPPING:
            self._st_traveled_d = params.d_traveled_m - self._st_ini_d
            final_d = self._st_stop_d
            v_out = calc_v(
                self._st_traveled_d,
                self._st_ini_v,
                0,
                final_d
            )

            if v_out <= self._params.zero_threshold_v:
                v_out = 0

            self._v_out = v_out
        elif self._state == self.State.STOPPED:
            self._v_out = 0
        elif self._state == self.State.RESUME:
            # self._st_traveled_d = params.d_traveled_m - self._st_ini_d
            # v_out = calc_v(self._st_traveled_d,0,self._params.cruise_v_limit,RESUME_D)
            # self._v_out = v_out
            pass

        if self._v_out is not None:
            # kph to m/s
            self._v_out = self._v_out

    def _update_a(self, params: UpdateParams):
        
        self._a_out = None
        
        if self._state == self.State.STOPPING:
            if self._v_out <= self._params.zero_threshold_v:
                self._a_out = -1.0
        elif self._state == self.State.STOPPED:
            self._a_out = -1.0
        elif self._state == self.State.RESUME:
            self._a_out = self._params.resume_a
        

    # == To string == #
    def __str__(self):
        return (
            f"state={self._state}, "
            f"cruise_v_out={self.cruise_v}, "
            f"v={self.v_ms}, "
            f"a={self.a_ms})"
        )

    # == Distances == #
    # TODO: Change input params. Put gps_data
    def _d_nxt_stop(self, d_trv: int) -> int:
        return self._stop_pts[self._stop_pt_idx] - d_trv



