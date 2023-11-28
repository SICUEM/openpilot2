#!/usr/bin/env python3
import json
import sys

from openpilot.common.params import Params

if __name__ == "__main__":
  params = Params()

  # set from google maps url
  if len(sys.argv) > 1:
    coords = sys.argv[1].split("/@")[-1].split("/")[0].split(",")
    dest = {
      "latitude": float(coords[0]),
      "longitude": float(coords[1])
    }
    params.put("NavDestination", json.dumps(dest))
    params.remove("NavDestinationWaypoints")
  else:
    print("Setting to rotonda")
    dest = {
      "latitude": -3.916862,
      "longitude": 40.370659,
    }
    params.put("NavDestination", json.dumps(dest))

    waypoints = [
      (40.370659, -3.916862),
    ]
    params.put("NavDestinationWaypoints", json.dumps(waypoints))

    print(dest)
    print(waypoints)
