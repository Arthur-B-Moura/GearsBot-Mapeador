#!/usr/bin/env python3

# Import the necessary libraries
import time
import math

from ev3dev2.motor import *       # MoveTank(), MoveSteering(), LargeMotor()
from ev3dev2.sensor.lego import * # GyroSensor(), LaserRangeSensor(), GPSSensor()
from ev3dev2.sound import Sound

from ev3dev2.sensor import *
from ev3dev2.sensor.virtual import *

# Define motores de acordo com os atuadores de saída
motor_esquerdo = LargeMotor(OUTPUT_A) # Motor da roda esquerda
motor_direito  = LargeMotor(OUTPUT_B) # Motor da roda direita
motor_lidar    = LargeMotor(OUTPUT_C) # Motor que gira o lidar

# Define sensores de localizacao geoespacial
sensor_giro  = GyroSensor(INPUT_6)       # Sensor giroscopio
sensor_lidar = LaserRangeSensor(INPUT_7) # Sensor lidar (distancia)
sensor_gps   = GPSSensor(INPUT_8)        # Sensor GPS

# Modulos/Funcoes basicas de movimento do tanque
controle_tanque = MoveTank(OUTPUT_A, OUTPUT_B)     # Movimento retilineo
controle_direct = MoveSteering(OUTPUT_A, OUTPUT_B) # Movimento com curva

#
alto_falante = Sound()

# Constantes e valores importantes
ANGULO_GIRO_LIDAR = 90
QTD_MEDIDAS_LIDAR = int(360/ANGULO_GIRO_LIDAR)

TAMANHO_GRID_CM = 50

P_INICIAL = [sensor_gps.x, sensor_gps.y]


######################
# Codigo não editado #
######################
touch_sensor_in1 = TouchSensor(INPUT_1)
touch_sensor_in2 = TouchSensor(INPUT_2)
touch_sensor_in3 = TouchSensor(INPUT_3)
touch_sensor_in4 = TouchSensor(INPUT_4)
#############################
# Fim do codigo não editado #
#############################

class Mapa:
    matriz = [[],[]]
    las_pos = []


# Mapeia QTD_MEDIDAS_LIDAR pontos de distancia
def Obtem_Distancias():
    # TODO: ajustar angulo de inicio a partir do valor do giroscopio
    distancias = []
    
    # Para todos os angulos dentro da resolucao
    for i in range(QTD_MEDIDAS_LIDAR): 
        medida = sensor_lidar.distance_centimeters # Le valor
        distancias.append(medida) # Salva valor lido no array
        
        # Move o sensor lidar de acordo com o angulo dado    
        motor_lidar.run_to_rel_pos(position_sp=ANGULO_GIRO_LIDAR,speed_sp=50)
        time.sleep(3)
    
    return distancias


# def Atualiza_Mapa_Hit(delta_pos, coord, distancias, mapa_hit):
# TODO: Ajustar arredondamento de valores para tamanho do mapa
# TODO: desenhar paredes nos QTD_MEDIDAS_LIDAR pontos 
def Atualiza_Mapa_Hit(delta_pos, distancias):
    y = []
    x = []
    
    for i in range(QTD_MEDIDAS_LIDAR):
        # Obtem angulo em graus e converte para radianos
        ang_deg = 90-(ANGULO_GIRO_LIDAR*i)
        ang_rad = math.radians(ang_deg)
        
        # print("sin = ", math.sin(ang_rad))
        # print("ang = ", ang_deg)
        
        y_ = ((distancias[i]*(math.sin(ang_rad)))+delta_pos[1])
        x_ = ((distancias[i]*(math.cos(ang_rad)))+delta_pos[0])
        
        # Calcula modulos x e y para os vetores de distancia obtidos
        y.append(round(y_/TAMANHO_GRID_CM))
        x.append(round(x_/TAMANHO_GRID_CM)) 
        
    # print("y = ", y)
    # print("x = ", x)

    maiores = [max(x),max(y)] # Posicoes limite Norte e Leste
    menores = [min(x),min(y)] # Posições limite   Sul e Oeste

    # Tamanho da grid de acordo com leitura
    # +1 para considerar o espaco em que o robo esta
    x_size = int(maiores[0]+abs(menores[0]))+1
    y_size = int(maiores[1]+abs(menores[1]))+1
    
    # print(f"x_size = {x_size}")
    # print(f"y_size = {y_size}")

    mapa_hit = [[0 for _ in range(x_size)]for _ in range(y_size)]
     
    # print("pos x =", x_size-maiores[0]-1)
    # print("pos y =", maiores[1])
    
    # Marca posicao do robo na grid
    mapa_hit[maiores[1]][x_size-maiores[0]-1] = 1
    
    return mapa_hit


print("="*50+"\n\n")


# Loop principal
while True:
    delta_pos_atual = [sensor_gps.x-P_INICIAL[0], sensor_gps.y-P_INICIAL[1]]
    print("posicao =", delta_pos_atual)
    
    medidas = Obtem_Distancias()
    print(medidas)
    print("\n")
    
    mapa_1 = Atualiza_Mapa_Hit(delta_pos_atual, medidas)
    
    for line in mapa_1:
        print(line)
