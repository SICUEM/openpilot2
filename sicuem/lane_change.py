import threading
from openpilot.common.params import Params


def trigger_lane_change_left():
  params = Params()
  params.put_bool("ForceLaneChangeLeft", True)
  print("🚗 Señal de cambio de carril izquierdo enviada.")

  def reset_flag():
    # Espera 1 segundo y luego resetea
    import time
    time.sleep(1)
    params.put_bool("ForceLaneChangeLeft", False)
    print("✅ Señal de cambio de carril reiniciada.")

  threading.Thread(target=reset_flag).start()


trigger_lane_change_left()
