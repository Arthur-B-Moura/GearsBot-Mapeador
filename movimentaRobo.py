#!/usr/bin/env python3

# Import the necessary libraries
import time
import math
from mapas import Mapa

from ev3dev2.motor import *       # MoveTank(), MoveSteering(), LargeMotor()
from ev3dev2.sensor.lego import * # GyroSensor(), LaserRangeSensor(), GPSSensor()
from ev3dev2.sound import Sound

from ev3dev2.sensor import *
from ev3dev2.sensor.virtual import *

# Define motores de acordo com os atuadores de saída
motor_esquerdo = LargeMotor(OUTPUT_A) # Motor da roda esquerda
motor_direito  = LargeMotor(OUTPUT_B) # Motor da roda direita

# Define sensores de localizacao geoespacial
sensor_giro  = GyroSensor(INPUT_6)       # Sensor giroscopio
sensor_lidar = LaserRangeSensor(INPUT_7) # Sensor lidar (distancia)
sensor_gps   = GPSSensor(INPUT_8)        # Sensor GPS

# Modulos/Funcoes basicas de movimento do tanque
controle_tanque = MoveTank(OUTPUT_A, OUTPUT_B)     # Movimento retilineo
controle_direct = MoveSteering(OUTPUT_A, OUTPUT_B) # Movimento com curva

# Caminho do Robô
# caminho = vetorCaminho

def Movimento_Robo(caminho):
    while caminho:
      print("len(caminho[0]) = ", len(caminho[0]))
      print("len(caminho) = ", len(caminho))
      
      if len(caminho) > 1:
        direcao = [caminho[0][i] - caminho[1][i] for i in range(len(caminho[0]))] # [1,0] = Ir para frente | [-1,0] = Ir para trás | [0,1] = Ir para a esquerda | [0,-1] = Ir para a direita
      else: break
      
      caminho.pop(0) # Tira o primeiro elemento do caminho
      
      if direcao[0] != 0:
          angle = sensor_giro.angle
          if abs(angle) - 0 > 3:
              controle_direct.on_for_degrees(steering = -angle , speed=2, degrees=180)
              time.sleep(300/1000)
              
          controle_direct.on_for_seconds(steering = 0, speed=17 * direcao[0] , seconds=2.7)
          time.sleep(300/1000)
          
      if direcao[1] != 0:
          controle_direct.on_for_degrees(steering = -90 * direcao[1], speed=18, degrees=180)
          time.sleep(500/1000)
          
          angle = sensor_giro.angle
          if abs(angle - 90) > 3 and direcao[1] == -1:
              controle_direct.on_for_degrees(steering = -(angle-90) , speed=2, degrees=180)
              time.sleep(300/1000)
              
          if abs(angle + 90) > 3 and direcao[1] == 1:
              controle_direct.on_for_degrees(steering = -(angle+90) , speed=2, degrees=180)
              time.sleep(300/1000)
    
          controle_direct.on_for_seconds(steering = 0, speed=17 , seconds=2.7)
          time.sleep(300/1000)
        
          controle_direct.on_for_degrees(steering=90 * direcao[1], speed=18, degrees=180)
        
      time.sleep(1)
