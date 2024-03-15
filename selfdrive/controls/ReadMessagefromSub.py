#!/usr/bin/env python3
import datetime
import sys
 
import requests
import paramiko
import paho.mqtt.client as mqtt
 
import cereal.messaging as messaging
 
class ReadMessagefromSub:
 
  def _init_(self):
    try:
      #broker_address = "192.168.1.184"
      broker_address="iot.eclipse.org" #use external broker
      client = mqtt.Client("P1")  # create new instance
      client.connect(broker_address)  # connect to broker
      client.publish("house/main-light", "OFF")  # publish
    except Exception as e:
      print(f"Ha ocurrido un error_________: {str(e)}")
      print(f"Ha ocurrido un error_________: {str(e)}")
      print(f"Ha ocurrido un error_________: {str(e)}")
      print(f"Ha ocurrido un error_________: {str(e)}")
 
  def crear_txt_ssh(self,ip, puerto, usuario, contraseña, nombre_archivo, contenido):
    cliente_ssh = paramiko.SSHClient()
    cliente_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
 
    try:
      cliente_ssh.connect(ip, port=puerto, username=usuario, password=contraseña)
      stdin, stdout, stderr = cliente_ssh.exec_command(f'echo "{contenido}" > {nombre_archivo}.txt')
    except Exception as e:
      print(f"Ha ocurrido un error: {str(e)}")
    finally:
      cliente_ssh.close()
 
  import paramiko
 
  def añadir_contenido_txt_ssh(self, nombre_archivo, contenido):
    try:
 
 
      # Comando para añadir el contenido al archivo existente
      stdin, stdout, stderr = self.cliente_ssh.exec_command(f'echo "{contenido}" >> {nombre_archivo}.txt')
 
      # Verificar si hubo errores
      if stderr.channel.recv_exit_status() != 0:
        print(f"Error al añadir contenido al archivo {nombre_archivo}.txt")
      else:
        print(f"Contenido añadido correctamente al archivo {nombre_archivo}.txt")
 
    except Exception as e:
      print(f"Ha ocurrido un error: {str(e)}")
    finally:
      print("Cerrando la conexión SSH")
      #self.cliente_ssh.close()
 
 
  def setCanalControlsd(self, sn):
    self.sm = sn
    self.cliente_ssh = paramiko.SSHClient()
    self.cliente_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    self.cliente_ssh.connect('195.235.211.197', port=22024, username='samuelortega', password='Steam.2024')
 
    self.crear_txt_ssh('195.235.211.197', 22024, 'samuelortega', 'Steam.2024', 'TELEMETRIA_OP', self.escribirEnTxtServ())
 
  def enviarAArchivo(self):
    self.añadir_contenido_txt_ssh( 'TELEMETRIA_OP', self.escribirEnTxtServ())
 
 
  def escribirEnTxtServ(self):
 
    return ("--------------------------------\n"+
            "Fecha: " + str(datetime.datetime.now()) + "\n"+
            "gpsLocationExternal: " + str(self.sm['gpsLocationExternal'])+"\n"+
                                       "--------------------------------\n")
