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
VELOCIDADE_GIRO_LIDAR = 40

TAMANHO_GRID_CM = 50

QTD_MEDIDAS_LIDAR = int(360/ANGULO_GIRO_LIDAR)
P_INICIAL = [sensor_gps.x, sensor_gps.y]

POS_X = 0
POS_Y = 1

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


# Mapeia QTD_MEDIDAS_LIDAR pontos de distancia
def Obtem_Distancias(giro_robo):
    # TODO: ajustar angulo de inicio a partir do valor do giroscopio
    distancias = []
    
    # Ajusta posicao do lidar
    motor_lidar.on_to_position(speed=VELOCIDADE_GIRO_LIDAR,position=(-giro_robo))
    
    # Para todos os angulos dentro da resolucao
    for i in range(QTD_MEDIDAS_LIDAR): 
        medida = sensor_lidar.distance_centimeters # Le valor
        distancias.append(medida) # Salva valor lido no array
        
        # Move o sensor lidar de acordo com o angulo dado    
        motor_lidar.on_to_position(position=ANGULO_GIRO_LIDAR*(i+1),speed=VELOCIDADE_GIRO_LIDAR)
        time.sleep(1)
        
    return distancias


def Distancias_Para_Coordenada(distancias, delta_pos):
    y = []
    x = []
    
    for i in range(QTD_MEDIDAS_LIDAR):
        # Obtem angulo em graus e converte para radianos
        ang_deg = 90-(ANGULO_GIRO_LIDAR*i) # Graus
        ang_rad = math.radians(ang_deg)    # Radianos
        
        y_ = ((distancias[i]*(math.sin(ang_rad)))+delta_pos[1])
        x_ = ((distancias[i]*(math.cos(ang_rad)))+delta_pos[0])
        
        # Calcula modulos x e y para os vetores de distancia obtidos
        y.append(round(y_/TAMANHO_GRID_CM))
        x.append(round(x_/TAMANHO_GRID_CM)) 
    
    dist = [x,y]
    return dist


# def Atualiza_Mapa_Hit(delta_pos, coord, distancias, mapa_hit):
# TODO: conferir e aprimorar coordenadas das paredes
# TODO: marcar -1 para desconhecido
def Cria_Mapa_Distancias(delta_pos, raw_values):
    
    dist = Distancias_Para_Coordenada(raw_values, delta_pos)
    
    x = dist[POS_X]
    y = dist[POS_Y]

    # print("y = ", y)
    # print("x = ", x)

    maiores = [max(x),max(y)] # Posicoes limite Norte e Leste
    menores = [min(x),min(y)] # Posições limite   Sul e Oeste

    print("Maiores = ", maiores)
    # Tamanho da grid de acordo com leitura
    # +1 para considerar o espaco em que o robo esta
    # +2 para considerar as paredes
    x_size = int(maiores[0]+abs(menores[0]))+1+2
    y_size = int(maiores[1]+abs(menores[1]))+1+2
    
    print(f"x_size = {x_size}")
    print(f"y_size = {y_size}")

    # Cria matriz de acordo com tamanho
    mapa_hit = [[0 for _ in range(x_size)]for _ in range(y_size)] 
    
    # Marca posicao do robo na grid
    x_robo = maiores[1]+1
    y_robo = x_size-maiores[0]-2
    mapa_hit[x_robo][y_robo] = 2
    
    # Marca paredes
    for val in zip(x,y):
        
        x1 = x_robo+val[0]+1   if val[0] > 0 else x_robo if val[0] == 0 else x_robo+val[0]+1
        y1 = (val[1]-y_robo)+3 if val[1] > 0 else y_robo if val[1] == 0 else (y_robo-val[1])+1
        
        print(x1, y1)
        mapa_hit[x1][y1] = 1
    
    return mapa_hit


print("="*50+"\n\n")

# Inicializa mapas de hit e miss
hits = Mapa()
miss = Mapa()


# Loop principal
while True:
    delta_pos_atual = [sensor_gps.x-P_INICIAL[0], sensor_gps.y-P_INICIAL[1]]
    angulo          = sensor_giro.angle # Obtem angulo atual
    
    # print("posicao =", delta_pos_atual)
    # print("angulo  =", angulo)
    
    medidas = Obtem_Distancias(angulo)
    # print(medidas)
    # print("\n")
    
    mapa_1 = Cria_Mapa_Distancias(delta_pos_atual, medidas)
    
    for line in mapa_1:
        print(line)
