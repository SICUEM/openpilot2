#!/usr/bin/env python3
import sys
import os
import cereal.messaging as messaging

class LaneChangeHandler:
    def __init__(self):
        self.pm = messaging.PubMaster(['laneChangeCommand'])

    def handle_lane_change(self, direction):
        if direction == "right":
            self.publish_lane_change_command('cambiarADer', True, True)
        elif direction == "left":
            self.publish_lane_change_command('cambiarAIzq', True, True)
        else:
            print("Dirección inválida. Usa 'left' o 'right'.")

    def publish_lane_change_command(self, field, state, activate_blinker):
        msg = messaging.new_message('laneChangeCommand')
        if field == 'cambiarADer':
            msg.laneChangeCommand.cambiarADer = state
        elif field == 'cambiarAIzq':
            msg.laneChangeCommand.cambiarAIzq = state
        msg.laneChangeCommand.activateBlinker = activate_blinker
        self.pm.send('laneChangeCommand', msg)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 lane_change.py [left|right]")
        sys.exit(1)

    # Update PWD environment variable to match the current directory
    os.environ['PWD'] = os.getcwd()

    direction = sys.argv[1].lower()
    handler = LaneChangeHandler()
    handler.handle_lane_change(direction)
