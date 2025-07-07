from cereal import log
from openpilot.common.conversions import Conversions as CV
from openpilot.common.params import Params
from openpilot.common.realtime import DT_MDL
from openpilot.selfdrive.controls.lib.drive_helpers import get_road_edge
from openpilot.selfdrive.modeld.custom_model_metadata import CustomModelMetadata, ModelCapabilities
from sicuem.adelantamiento import should_start_overtake, get_overtake_command

LaneChangeState = log.LaneChangeState
LaneChangeDirection = log.LaneChangeDirection

LANE_CHANGE_SPEED_MIN = 20 * CV.MPH_TO_MS
LANE_CHANGE_TIME_MAX = 10.

DESIRES = {
  LaneChangeDirection.none: {
    LaneChangeState.off: log.Desire.none,
    LaneChangeState.preLaneChange: log.Desire.none,
    LaneChangeState.laneChangeStarting: log.Desire.none,
    LaneChangeState.laneChangeFinishing: log.Desire.none,
  },
  LaneChangeDirection.left: {
    LaneChangeState.off: log.Desire.none,
    LaneChangeState.preLaneChange: log.Desire.none,
    LaneChangeState.laneChangeStarting: log.Desire.laneChangeLeft,
    LaneChangeState.laneChangeFinishing: log.Desire.laneChangeLeft,
  },
  LaneChangeDirection.right: {
    LaneChangeState.off: log.Desire.none,
    LaneChangeState.preLaneChange: log.Desire.none,
    LaneChangeState.laneChangeStarting: log.Desire.laneChangeRight,
    LaneChangeState.laneChangeFinishing: log.Desire.laneChangeRight,
  },
}

AUTO_LANE_CHANGE_TIMER = {
  -1: 0.0,
  0: 0.0,
  1: 0.1,
  2: 0.5,
  3: 1.0,
  4: 1.5,
}

def get_min_lateral_speed(value: int, is_metric: bool, default: float = LANE_CHANGE_SPEED_MIN):
  speed: float = default if value == 0 else value * CV.KPH_TO_MS if is_metric else CV.MPH_TO_MS
  return speed

class DesireHelper:
  def __init__(self):
    self.lane_change_state = LaneChangeState.off
    self.lane_change_direction = LaneChangeDirection.none
    self.lane_change_timer = 0.0
    self.lane_change_ll_prob = 1.0
    self.keep_pulse_timer = 0.0
    self.prev_one_blinker = False
    self.desire = log.Desire.none

    self.param_s = Params()
    self.lane_change_wait_timer = 0
    self.prev_lane_change = False
    self.prev_brake_pressed = False
    self.road_edge = False
    self.param_read_counter = 0
    self.edge_toggle = self.param_s.get_bool("RoadEdge")
    self.lane_change_set_timer = int(self.param_s.get("AutoLaneChangeTimer", encoding="utf8"))
    self.lane_change_bsm_delay = self.param_s.get_bool("AutoLaneChangeBsmDelay")

    self.custom_model_metadata = CustomModelMetadata(params=self.param_s, init_only=True)
    self.model_use_lateral_planner = self.custom_model_metadata.valid and \
                                     self.custom_model_metadata.capabilities & ModelCapabilities.LateralPlannerSolution

    self.overtake_active = False
    self.overtake_timer = 0.0
    self.overtake_speed_delta = 0.0
    self.overtake_v_cruise_last = None

  def read_param(self):
    self.edge_toggle = self.param_s.get_bool("RoadEdge")
    self.lane_change_set_timer = int(self.param_s.get("AutoLaneChangeTimer", encoding="utf8"))
    self.lane_change_bsm_delay = self.param_s.get_bool("AutoLaneChangeBsmDelay")

  def update(self, carstate, lateral_active, lane_change_prob, model_data=None, lat_plan_sp=None, desire_override=None, radar_state=None):

    override_blinker = self.param_s.get_bool("c_carril")
    if desire_override is not None:
      self.desire = desire_override
      return

    if self.param_read_counter % 50 == 0:
      self.read_param()
    self.param_read_counter += 1
    lane_change_auto_timer = AUTO_LANE_CHANGE_TIMER.get(self.lane_change_set_timer, 2.0)
    v_ego = carstate.vEgo
    one_blinker = carstate.leftBlinker != carstate.rightBlinker

    # 🚨 Forzado directo del cambio de carril (sin intermitente ni torque) si está activado c_carril
    if self.param_s.get_bool("c_carril"):
      if self.param_s.get_bool("ForceLaneChangeLeft") and self.lane_change_state == LaneChangeState.off:
        self.lane_change_direction = LaneChangeDirection.left
        blindspot = carstate.leftBlindspot
        if blindspot:
          cloudlog.warning("🔴 Cambio a izquierda bloqueado por ángulo muerto")
          self.param_s.put_bool("ForceLaneChangeLeft", False)
          return
        else:
          self.lane_change_state = LaneChangeState.laneChangeStarting
          self.lane_change_ll_prob = 1.0
          self.lane_change_wait_timer = 0
          self.param_s.put_bool("ForceLaneChangeLeft", False)
          return

      if self.param_s.get_bool("ForceLaneChangeRight") and self.lane_change_state == LaneChangeState.off:
        self.lane_change_direction = LaneChangeDirection.right
        blindspot = carstate.rightBlindspot
        if blindspot:
          cloudlog.warning("🔴 Cambio a derecha bloqueado por ángulo muerto")
          self.param_s.put_bool("ForceLaneChangeRight", False)
          return
        else:
          self.lane_change_state = LaneChangeState.laneChangeStarting
          self.lane_change_ll_prob = 1.0
          self.lane_change_wait_timer = 0
          self.param_s.put_bool("ForceLaneChangeRight", False)
          return

    '''# 🚨 Forzado manual (sin intermitente) si está activado c_carril ----(preLaneChange)
    if self.param_s.get_bool("c_carril"):
      if self.param_s.get_bool("ForceLaneChangeLeft") and self.lane_change_state == LaneChangeState.off:
        self.lane_change_direction = LaneChangeDirection.left
        self.lane_change_state = LaneChangeState.preLaneChange
        self.lane_change_ll_prob = 1.0
        self.lane_change_wait_timer = 0
        self.param_s.put_bool("ForceLaneChangeLeft", False)
        return

      if self.param_s.get_bool("ForceLaneChangeRight") and self.lane_change_state == LaneChangeState.off:
        self.lane_change_direction = LaneChangeDirection.right
        self.lane_change_state = LaneChangeState.preLaneChange
        self.lane_change_ll_prob = 1.0
        self.lane_change_wait_timer = 0
        self.param_s.put_bool("ForceLaneChangeRight", False)
        return'''
    # 🚘 Adelantamiento automático por diferencia de velocidad y distancia (hecho por Adrián)

    from openpilot.common.swaglog import cloudlog

    # 🧠 Adelantamiento automático con retorno al carril derecho
    if radar_state is not None and self.param_s.get_bool("sic_adelantar"):
      try:
        if not self.overtake_active and should_start_overtake(carstate, radar_state):
          self.lane_change_direction, self.lane_change_state = get_overtake_command()
          self.lane_change_ll_prob = 1.0
          self.lane_change_wait_timer = 0
          self.overtake_active = True
          self.overtake_timer = 0.0
          self.overtake_v_cruise_last = carstate.cruiseSpeed
          self.overtake_speed_delta = 5.55  # +20 km/h
          Params().put("OverrideCruiseSpeed", str(self.overtake_v_cruise_last + self.overtake_speed_delta))
          cloudlog.info("🟢 Adelantamiento automático activado (+20 km/h)")

        elif self.overtake_active:
          self.overtake_timer += DT_MDL
          if self.overtake_timer > 5.0 and self.lane_change_state in (LaneChangeState.off,
                                                                      LaneChangeState.laneChangeFinishing):
            self.lane_change_direction = LaneChangeDirection.right
            self.lane_change_state = LaneChangeState.laneChangeStarting
            cloudlog.info("🔄 Retorno automático al carril derecho tras adelantamiento")

          if self.overtake_timer > 10.0:
            self.overtake_active = False
            if self.overtake_v_cruise_last is not None:
              Params().put("OverrideCruiseSpeed", str(self.overtake_v_cruise_last))
              cloudlog.info("✅ Restablecida velocidad original tras adelantamiento")

      except Exception as e:
        cloudlog.error(f"❌ Error en lógica de adelantamiento: {e}")

    # TODO: SP: !659: User-defined minimum lane change speed
    below_lane_change_speed = v_ego < LANE_CHANGE_SPEED_MIN

    if self.model_use_lateral_planner:
      self.road_edge = get_road_edge(carstate, model_data, self.edge_toggle)

    if not lateral_active or self.lane_change_timer > LANE_CHANGE_TIME_MAX or self.lane_change_set_timer == -1:
      self.lane_change_state = LaneChangeState.off
      self.lane_change_direction = LaneChangeDirection.none
      self.prev_lane_change = False
      self.prev_brake_pressed = False
    else:
      # LaneChangeState.off
      if self.lane_change_state == LaneChangeState.off and one_blinker and not self.prev_one_blinker and not below_lane_change_speed:
        self.lane_change_state = LaneChangeState.preLaneChange
        self.lane_change_ll_prob = 1.0
        self.lane_change_wait_timer = 0

      # LaneChangeState.preLaneChange
      elif self.lane_change_state == LaneChangeState.preLaneChange and (self.road_edge if self.model_use_lateral_planner else lat_plan_sp.laneChangeEdgeBlockDEPRECATED):
        self.lane_change_direction = LaneChangeDirection.none
      elif self.lane_change_state == LaneChangeState.preLaneChange:
        # Set lane change direction
        self.lane_change_direction = LaneChangeDirection.left if \
          carstate.leftBlinker else LaneChangeDirection.right

        torque_applied = carstate.steeringPressed and \
                         ((carstate.steeringTorque > 0 and self.lane_change_direction == LaneChangeDirection.left) or
                          (carstate.steeringTorque < 0 and self.lane_change_direction == LaneChangeDirection.right))

        blindspot_detected = ((carstate.leftBlindspot and self.lane_change_direction == LaneChangeDirection.left) or
                              (carstate.rightBlindspot and self.lane_change_direction == LaneChangeDirection.right))

        self.lane_change_wait_timer += DT_MDL

        if self.lane_change_bsm_delay and blindspot_detected and lane_change_auto_timer:
          if lane_change_auto_timer == 0.1:
            self.lane_change_wait_timer = -1
          else:
            self.lane_change_wait_timer = lane_change_auto_timer - 1

        auto_lane_change_allowed = lane_change_auto_timer and self.lane_change_wait_timer > lane_change_auto_timer

        if carstate.brakePressed and not self.prev_brake_pressed:
          self.prev_brake_pressed = carstate.brakePressed

        if not one_blinker or below_lane_change_speed:
          self.lane_change_state = LaneChangeState.off
          self.lane_change_direction = LaneChangeDirection.none
          self.prev_lane_change = False
          self.prev_brake_pressed = False
        elif (torque_applied or (auto_lane_change_allowed and not self.prev_lane_change and not self.prev_brake_pressed)) and \
          not blindspot_detected:
          self.lane_change_state = LaneChangeState.laneChangeStarting
          self.prev_lane_change = True

      # LaneChangeState.laneChangeStarting
      elif self.lane_change_state == LaneChangeState.laneChangeStarting:
        # fade out over .5s
        self.lane_change_ll_prob = max(self.lane_change_ll_prob - 2 * DT_MDL, 0.0)

        # 98% certainty
        if lane_change_prob < 0.02 and self.lane_change_ll_prob < 0.01:
          self.lane_change_state = LaneChangeState.laneChangeFinishing

      # LaneChangeState.laneChangeFinishing
      elif self.lane_change_state == LaneChangeState.laneChangeFinishing:
        # fade in laneline over 1s
        self.lane_change_ll_prob = min(self.lane_change_ll_prob + DT_MDL, 1.0)

        if self.lane_change_ll_prob > 0.99:
          self.lane_change_direction = LaneChangeDirection.none
          if one_blinker:
            self.lane_change_state = LaneChangeState.preLaneChange
          else:
            self.lane_change_state = LaneChangeState.off
            self.prev_lane_change = False
            self.prev_brake_pressed = False

    if self.lane_change_state in (LaneChangeState.off, LaneChangeState.preLaneChange):
      self.lane_change_timer = 0.0
    else:
      self.lane_change_timer += DT_MDL

    self.prev_one_blinker = one_blinker

    self.desire = DESIRES[self.lane_change_direction][self.lane_change_state]

    # Send keep pulse once per second during LaneChangeStart.preLaneChange
    if self.lane_change_state in (LaneChangeState.off, LaneChangeState.laneChangeStarting):
      self.keep_pulse_timer = 0.0
    elif self.lane_change_state == LaneChangeState.preLaneChange:
      self.keep_pulse_timer += DT_MDL
      if self.keep_pulse_timer > 1.0:
        self.keep_pulse_timer = 0.0
      elif self.desire in (log.Desire.keepLeft, log.Desire.keepRight):
        self.desire = log.Desire.none
