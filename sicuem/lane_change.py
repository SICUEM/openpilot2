from openpilot.common.params import Params

params = Params()
params.put_bool("ForceLaneChangeLeft", True)
print("¡Solicitud de cambio de carril izquierdo enviada!")
