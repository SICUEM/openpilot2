#!/usr/bin/env python3
import sys
import cereal.messaging as messaging
from cereal import log

Desire = log.Desire

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 lane_change.py [left|right]")
        sys.exit(1)

    direction = sys.argv[1]
    pm = messaging.PubMaster(['laneChangeCommand'])

    dat = messaging.new_message('laneChangeCommand')
    if direction == "left":
        dat.laneChangeCommand.direction = Desire.laneChangeLeft
    elif direction == "right":
        dat.laneChangeCommand.direction = Desire.laneChangeRight
    else:
        print("Dirección inválida. Usa 'left' o 'right'.")
        sys.exit(1)

    pm.send('laneChangeCommand', dat)
    print(f"Enviado comando de cambio de carril: {direction}")
