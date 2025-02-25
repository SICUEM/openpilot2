#!/usr/bin/env python3
import sys
import time
import cereal.messaging as messaging
from cereal import log

Desire = log.Desire
LaneChangeState = log.LaneChangeState  # Importamos los estados de cambio de carril

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 lane_change.py [left|right]")
        sys.exit(1)

    direction = sys.argv[1].lower()
    if direction not in ["left", "right"]:
        print("Dirección inválida. Usa 'left' o 'right'.")
        sys.exit(1)

    # Publicador de mensajes
    pm = messaging.PubMaster(['laneChangeCommand'])

    # Crear mensaje de cambio de carril
    lane_change_msg = messaging.new_message('laneChangeCommand')

    # Configurar la dirección y el estado inicial del cambio de carril
    lane_change_msg.laneChangeCommand.direction = (
        Desire.laneChangeLeft if direction == "left" else Desire.laneChangeRight
    )
    lane_change_msg.laneChangeCommand.state = LaneChangeState.preLaneChange  # ← Estado correcto
    lane_change_msg.laneChangeCommand.activateBlinker = True  # ← Activar intermitente

    # Enviar el mensaje varias veces para asegurar recepción
    for _ in range(5):
        pm.send('laneChangeCommand', lane_change_msg)
        print(f"🚗 Enviando comando de cambio de carril hacia {direction}... (Estado: preLaneChange, Intermitente activado)")
        time.sleep(0.1)  # Pequeña pausa para que OpenPilot lo reciba

    print(f"✅ Comando de cambio de carril enviado correctamente hacia {direction}.")
