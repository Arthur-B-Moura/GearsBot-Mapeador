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
ANGULO_GIRO_LIDAR = 15
VELOCIDADE_GIRO_LIDAR = 10

TAMANHO_GRID_CM = 50

QTD_MEDIDAS_LIDAR = int(360/ANGULO_GIRO_LIDAR)
P_INICIAL = [sensor_gps.x, sensor_gps.y]

POS_X = 0
POS_Y = 1

POS_NORTE = 0
POS_SUL   = 1
POS_LESTE = 2
POS_OESTE = 3

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
    # TODO: conferir ajuste do angulo de inicio a partir do valor do giroscopio
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


# Função que retorna as coordenadas (x,y), no referencial de uma matriz, de um vetor(dx,dy)
# cuja origem é um ponto centr(x,y) qualquer pertencente a esta matriz
def Muda_Referencia(vetor, centro):
    coord = [0,0]
    
    print("centro =", centro)
    print("vetor = ", vetor)
    
    coord[POS_X] = centro[POS_X] + vetor[POS_X]
    coord[POS_Y] = centro[POS_Y] - vetor[POS_Y]
    
    if coord[POS_X] < centro[POS_X] and coord[POS_X] != 0: coord[POS_X] -= 1
    if coord[POS_Y] < centro[POS_Y] and coord[POS_Y] != 0: coord[POS_Y] -= 1
    
    return coord


# def Atualiza_Mapa_Hit(delta_pos, coord, distancias, mapa_hit):
# TODO: conferir e aprimorar coordenadas das paredes
# TODO: marcar -1 para desconhecido
def Cria_Mapa_Distancias(delta_pos, raw_values):
    
    dist = Distancias_Para_Coordenada(raw_values, delta_pos)
    mapa = Mapa()
    
    x = dist[POS_X]
    y = dist[POS_Y]

    # print("y = ", y)
    # print("x = ", x)

    maiores = [max(x),max(y)] # Posicoes limite Leste e Norte
    menores = [min(x),min(y)] # Posições limite Oeste e Sul

    # Definindo tamanho do mapa (N,S,L,O) de acordo com o padrão da Classe Mapa()
    # +1 e -1 para considerar as paredes em cada direcao
    mapa.tam = [maiores[POS_Y]+1, abs(menores[POS_Y]-1), maiores[POS_X]+1, abs(menores[POS_X]-1)]
    
    # Tamanho da grid de acordo com leitura
    # +1 para considerar o espaco em que o robo esta
    y_size = int(mapa.tam[POS_NORTE] + mapa.tam[POS_SUL])+1   # Tamanho vertical   (Norte -> Sul)
    x_size = int(mapa.tam[POS_LESTE] + mapa.tam[POS_OESTE])+1 # Tamanho horizontal (Leste -> Oeste)
    
    # print(f"x_size = {x_size}")
    # print(f"y_size = {y_size}")

    # Cria matriz de acordo com tamanho
    mapa_hit    = [[0 for _ in range(x_size)]for _ in range(y_size)] 
    mapa.matriz = [[0 for _ in range(x_size)]for _ in range(y_size)] 
    
    # Define coordenadas do ponto de referência na matriz
    mapa.center[POS_X] =  mapa.tam[POS_OESTE] 
    mapa.center[POS_Y] =  mapa.tam[POS_NORTE] 
    
    print("Center coord = ", mapa.center)
    # print("Tam sizes (N S L O) = " ,mapa.tam)
    
    # ========= TEMP =============
    x_robo = maiores[1]+1
    y_robo = x_size-maiores[0]-2
    # ========= TEMP =============
    
    # Marca posicao do robo na grid
    mapa.matriz[mapa.center[POS_Y]][mapa.center[POS_X]] = -2
    
    # print("x = ", x)
    # print("y = ", y)
    
    
    for i in range(QTD_MEDIDAS_LIDAR):
        # Obtem angulo em graus e converte para radianos
        ang_deg = 90-(ANGULO_GIRO_LIDAR*i) # Graus
        ang_rad = math.radians(ang_deg)    # Radianos
        
        if ang_deg == 90 or ang_deg == -90: 
            val_x = 0
        else:
            val_x = math.ceil(math.cos(ang_rad)) if ang_deg < 180 else math.floor(math.cos(ang_rad))
        
        if ang_deg == 0 or ang_deg == -180: 
            val_y = 0
        else:
            val_y = math.ceil(math.sin(ang_rad)) if ang_deg < 90 and ang_deg > 270 else math.floor(math.sin(ang_rad))
        
        # print(f"ang_deg = {ang_deg}, val_x = {val_x}")
        # print(f"ang_deg = {ang_deg}, val_y = {val_y}")
        
        wall = Muda_Referencia([x[i]+val_x,y[i]+val_y], mapa.center)
        
        print(f"wall = ", wall)
        
        mapa.matriz[wall[POS_Y]][wall[POS_X]] += 1
 
    
    print("Mapa = ")
    print(mapa)
    
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
    
    # print("Mapa 2 =")
    # for line in mapa_1:
    #     print(line)
