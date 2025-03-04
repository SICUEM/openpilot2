#!/usr/bin/env python3
import sys
import time
import cereal.messaging as messaging
from cereal import log

Desire = log.Desire
LaneChangeState = log.LaneChangeState

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 lane_change.py [left|right]")
        sys.exit(1)

    direction = sys.argv[1].lower()
    if direction not in ["left", "right"]:
        print("❌ Dirección inválida. Usa 'left' o 'right'.")
        sys.exit(1)

    # Publicador de mensajes (Solo laneChangeCommand)
    pm = messaging.PubMaster(['laneChangeCommand'])

    # Crear mensaje de cambio de carril
    lane_change_msg = messaging.new_message('laneChangeCommand')
    lane_change_msg.laneChangeCommand.direction = (
        Desire.laneChangeLeft if direction == "left" else Desire.laneChangeRight
    )
    lane_change_msg.laneChangeCommand.state = LaneChangeState.preLaneChange
    lane_change_msg.laneChangeCommand.activateBlinker = True

    try:
        for _ in range(5):
            pm.send('laneChangeCommand', lane_change_msg)
            lane_change_msg.clear_write_flag()  # ✅ Limpia la bandera de escritura
            print(f"🚗 Enviando comando de cambio de carril hacia {direction}... (Estado: preLaneChange)")
            time.sleep(0.1)
    except Exception as e:
        print(f"❌ Error al enviar mensaje: {e}")
    finally:
        del pm  # Cierra el publicador

    print(f"✅ Comando de cambio de carril enviado correctamente hacia {direction}.")
