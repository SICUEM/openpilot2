ACTIVATION_D = 10   # Distancia del punto de activación (m)

CRUISE_V_MIN = 30   # Velocidad mínima de cruise (m)

IN_AREA_D = 60     # Radio de estado IN_AREA (m)
APPROACHING_D = 50 # Radio de estao APPROACHING (m)
STOPPING_D = 25     # Radio de estado STOPPING (m)
STOP_T = 10         # Tiempo de estado STOP (s)
RESUME_D = 60       # Longitud estado RESUME (m)

IN_AREA_V = 20      # Velocidad de estado IN_AREA (k/h)
APPROACHING_V = 10  # Velocidad de estado APPROACHING (k/h)
RESUME_V = 50       # Velocidad que se ha de 
                    # alcanzar en estado RESUME
RESUME_A = 1      # Aceleración aplicada en el 
                    # estado RESUME (m) (no se usa)
            
STOP_V_THRES = 1    # Umbral de velocidad a 0 (k/h)

STOP_POINTS = [100,400]    # Distancia a los puntos 
                                # de parada
                            
CRUISE_CONTROL = False       # Control de CRUISE activado

TELEM_SRV_IP = "192.168.1.15"    # IP del servidor de telemetría
TELEM_SRV_PORT ="9099"       # Puerto del servidor de telemetria
TELEM_ACTIVE = False         # Esta la telemetría activa ??
TELEM_CONN_DELAY = 5        # Delay de reconexión de socket ??
TELEM_FREQ = 2            # Con que frecuencia se actualiza la telemetria ??
