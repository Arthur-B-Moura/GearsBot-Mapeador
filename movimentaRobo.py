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

# Constantes
TAM_GRID_X = 10
TAM_GRID_Y = 10

def getPosition():
    x = sensor_gps.x
    y = sensor_gps.y
    return [x,y]

def Movimento_Robo(caminho):
    posAtual = getPosition()
    posPast = posAtual
    while caminho:

      print("len(caminho) = ", len(caminho))
      
      if len(caminho) > 1:
        direcao = [caminho[0][i] - caminho[1][i] for i in range(len(caminho[0]))] # [1,0] = Ir para frente | [-1,0] = Ir para trás | [0,1] = Ir para a esquerda | [0,-1] = Ir para a direita
      else: break
      
      caminho.pop(0) # Tira o primeiro elemento do caminho
      
      if direcao[1] != 0:
          angle = sensor_giro.angle
          if abs(angle) - 0 > 3:
              controle_direct.on_for_degrees(steering = -angle , speed=2, degrees=180)
              time.sleep(300/1000)
              
          while abs(posAtual[1]) - abs(posPast[1]) <= TAM_GRID_Y:
              motor_esquerdo.on(15)
              motor_direito.on(15)
              
          motor_esquerdo.off()
          motor_direito.off()
          posPast = posAtual
          posAtual = getPosition()
          
          time.sleep(300/1000)
          
          
      if direcao[0] != 0:
          controle_direct.on_for_degrees(steering = -90 * direcao[0], speed=18, degrees=180)
          time.sleep(500/1000)
          
          angle = sensor_giro.angle
          if abs(angle - 90) > 3 and direcao[0] == -1:
              controle_direct.on_for_degrees(steering = -(angle-90) , speed=2, degrees=180)
              time.sleep(300/1000)
              
          if abs(angle + 90) > 3 and direcao[0] == 1:
              controle_direct.on_for_degrees(steering = -(angle+90) , speed=2, degrees=180)
              time.sleep(300/1000)
    
          while abs(posAtual[0]) - abs(posPast[0]) <= TAM_GRID_X:
              motor_esquerdo.on(15)
              motor_direito.on(15)
              
          motor_esquerdo.off()
          motor_direito.off()
          posPast = posAtual
          posAtual = getPosition()
          time.sleep(300/1000)
        
          controle_direct.on_for_degrees(steering=90 * direcao[0], speed=18, degrees=180)
        
      time.sleep(1)
