# adelantamiento.py
# Adrián Cañadas Gallardo
# Lógica para lanzar el adelantamiento automático desde desire_helper

from cereal import log
from openpilot.common.params import Params

LaneChangeDirection = log.LaneChangeDirection
LaneChangeState = log.LaneChangeState

params = Params()

def should_start_overtake(carstate, radarstate):
  """
  Decide si se debe iniciar el adelantamiento automático.
  Requisitos:
  - Activado el toggle 'sic_adelantar'
  - Vehículo delante detectado (lead válido)
  - Diferencia de velocidad > 20 km/h (~5.5 m/s)
  - Menos de 50 metros de distancia
  - Carril izquierdo libre (sin ángulo muerto)
  """
  if not params.get_bool("sic_adelantar"):
    return False

  # 🚘 Verifica lead válido
  lead = radarstate.leads[0] if len(radarstate.leads) > 0 else None
  if lead is None or not lead.status:
    return False

  ego_v = carstate.vEgo       # nuestra velocidad actual [m/s]
  lead_v = lead.vLead         # velocidad del coche delante [m/s]
  d_rel = lead.dRel           # distancia al coche delante [m]

  # ✅ Condiciones para adelantar
  vel_diff_ok = (ego_v - lead_v) > 5.5     # Más de 20 km/h de diferencia
  distancia_ok = d_rel < 50                # Menos de 50 metros
  libre_izquierda = not carstate.leftBlindspot  # Sin vehículo al lado

  return vel_diff_ok and distancia_ok and libre_izquierda

def get_overtake_command():
  """
  Devuelve la dirección y el estado que se deben aplicar
  en DesireHelper para iniciar el cambio de carril.
  """
  return LaneChangeDirection.left, LaneChangeState.laneChangeStarting
