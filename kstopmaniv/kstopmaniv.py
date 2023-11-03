
from enum import Enum
import math
from kstopmaniv.kloggeriv import append_to_log_async, make_log_dir
from kstopmaniv.ktimersiv import KTimerIV
import numpy as np



# ===== LongControl link ==== #

class KSpeedMan:
    def __init__(self):
        self._v = None
    
    @property
    def v(self) -> float:
        return self._v
    
    @v.setter
    def v(self, value: float):
        self._v = value

    def reset(self):
        self._v = None



# ====== For Test purposes ===== #

LOG_DIR = "/tmp/klog"
LOG_FILE = "k.kstopmaniv.log"
LOG_FREQ = 0.5
LOG_TIMER = KTimerIV(LOG_FREQ)

make_log_dir(LOG_DIR)


def compute_desired_v(initial_v: int, final_v: int, final_distance: int, current_distance: int) -> float:
            k = -np.log(0.01) / final_distance  # Ajustar el valor para que y(final_distance) esté cerca de final_v
            desired_speed = (initial_v - final_v) * np.exp(-k * current_distance) + final_v
            return desired_speed


class KParamsIV:
    def __init__(self):
        # Distancia de activación
        self._activation_d: float = None
        # Velocidad por defecto del cruise (km/h)
        self._cruise_v_def: int = None
        # Velocidad final (km/h)
        self._final_v: int = 10
        # Distancia final (mts)
        self._final_d: int = 0
        self._resume_v: int = 0
        self._resume_d: int = 0

        self.read()
    
    def read(self):
        self._activation_d = 100    # m

        self._final_v = 10          # km/h
        self._final_d = 60          # m
        
        self._resume_v = 100        # km/h
        self._resume_d = 40         # m

        self._cruise_v_def = 35     # km/h

    @property
    def activation_d(self):
        return self._activation_d

    @property
    def cruise_v(self):
        return self._cruise_v_def

    @property
    def final_d(self):
        return self._final_d

    @property
    def final_v(self):
        return self._final_v 
    

class KStateIV(Enum):
    NO_ACTIVE = 0
    STOPPING = 1
    STOPPED = 2
    RESUME = 3
    DRIVING = 4


class KStopManIV:



    def __init__(self):
        self._params: KParamsIV = KParamsIV()
        self._state: KStateIV = KStateIV.NO_ACTIVE
        self._stop_flag: bool = False
        self._resume_flag: bool = False
        self._desired_v: float = None
        self._cruise_v: int = None
        self._state_init_v: float = None
        self._last_state: KStateIV = None

    # ====== ACCESORS ====== #
    @property
    def v(self) -> float:
        dv = None
        if self._desired_v is not None:
            dv = self._desired_v.item() / 3.6
        return dv
    
    @v.setter
    def v(self, value: float):
        self._desired_v = value

    
    @property
    def cruise_v(self) -> int:
        return self._cruise_v
    
    @cruise_v.setter
    def cruise_v(self, value: int):
        self._cruise_v = value


    # ======= OPs ======= #
    def update(self, traveled_d: float, current_v: int):

        self._update_state(traveled_d, current_v)
        self._calculate_v(traveled_d)
        

    def _update_state(self, traveled_d: float, current_v: int):
        self._last_state = self._state
        if self._state == None:
            self._state = KStateIV.NO_ACTIVE
        elif traveled_d >= self._params.activation_d and self._state == KStateIV.NO_ACTIVE:
            self._state = KStateIV.STOPPING
            self._state_init_v = math.floor(current_v * 3.6) # m/s to km/h
        elif self._state == KStateIV.STOPPING and current_v == 0:
            self._state = KStateIV.STOPPED
        elif self._state == KStateIV.STOPPED and self._resume_flag:
            self._state = KStateIV.RESUME
            self._resume_flag = False
        
        LOG_TIMER.update()
        if LOG_TIMER.flag:
            self._log_state(traveled_d)

    def _calculate_v(self, traveled_d: int) -> int:

        self.v = None

        if self._state == KStateIV.NO_ACTIVE:
            self.v = None
        elif self._state == KStateIV.STOPPING:
            self._calculate_stopping_v(traveled_d)
        elif self._state == KStateIV.STOPPED:
            self.v = 0

    def _calculate_cruise_v(self):
        if self._last_state != self._state:
            self._cruise_v = None
            if self._state == KStateIV.NO_ACTIVE:
                self._cruise_v = self._params.cruise_v  # km/h
        
    def _calculate_stopping_v(self, traveled_d: float):

        current_distance = math.floor(traveled_d - self._params.activation_d)

        self.v = compute_desired_v(self._state_init_v, self._params.final_v, self._params.final_d, current_distance)
        if self.v < (self._params.final_v + 1) * 3.6:
            self.v = np.float64(0)

    def _log_state(self, traveled_d: int):
        v_str = "--.--"
        if self.v is not None:
            v_str = f"{self.v:2f}"
        current_distance = traveled_d - self._params.activation_d
        msg = f"[TD]={traveled_d:1f} m::[V]={v_str} m/s::[CruV]={self.cruise_v} k/h::[CD]={math.floor(current_distance)}::[ST]={self._state} (ini -> {self._state_init_v})"
        append_to_log_async(msg, f"{LOG_DIR}/{LOG_FILE}")



    