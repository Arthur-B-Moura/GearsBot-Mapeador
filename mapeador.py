#!/usr/bin/env python3

# Import the necessary libraries
import time
import math

# Arquivos que devem ser carregados ao gearsbot
# o nome dos módulos, dentro do simulador, deve ser alterado de "module1.py" e "module2.py" para
# os nomes de arquivos utilizados abaixo, ou seja, "mapas.py" e "caminho.py"
from mapas   import Mapa            # mapas = mapas.py
from caminho import Movimento_Robo  # caminho = movimentaRobo.py

from ev3dev2.motor import *       # MoveTank(), MoveSteering(), LargeMotor()
from ev3dev2.sensor.lego import * # GyroSensor(), LaserRangeSensor(), GPSSensor()
from ev3dev2.sound import Sound

from ev3dev2.sensor import *
from ev3dev2.sensor.virtual import *

# --------------------- #
#  Sensores e atuadores #
# --------------------- #

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

touch_sensor_in1 = TouchSensor(INPUT_1)
touch_sensor_in2 = TouchSensor(INPUT_2)
touch_sensor_in3 = TouchSensor(INPUT_3)
touch_sensor_in4 = TouchSensor(INPUT_4)



# ------------------------- #
#  Valores de customização  #
# ------------------------- #
ANGULO_GIRO_LIDAR = 5
VELOCIDADE_GIRO_LIDAR = 10
LIDAR_SLEEP_TIME = 0.01

TAMANHO_GRID_CM = 15

# ------------ #
#  Constantes  #
# ------------ #
QTD_MEDIDAS_LIDAR = int(360/ANGULO_GIRO_LIDAR)
P_INICIAL = [sensor_gps.x, sensor_gps.y]

POS_X = 0
POS_Y = 1

POS_NORTE = 0
POS_SUL   = 1
POS_LESTE = 2
POS_OESTE = 3

# Inicializa mapas de hit, miss e unknown
hits    = Mapa()
miss    = Mapa()
unknown = Mapa()


#===========================#
#                           #
#  ~~~ Seção de Funções ~~~ #
#                           #
#===========================#

# --------------------------------------------- #
#  Mapeia QTD_MEDIDAS_LIDAR pontos de distancia #
# --------------------------------------------- #
def Obtem_Distancias(giro_robo):
    distancias = []
    
    # Ajusta posicao do lidar
    motor_lidar.on_to_position(speed=VELOCIDADE_GIRO_LIDAR,position=(-giro_robo))
    
    # Para todos os angulos dentro da resolucao
    for i in range(QTD_MEDIDAS_LIDAR): 
        medida = sensor_lidar.distance_centimeters # Le valor
        distancias.append(medida) # Salva valor lido no array
        
        # Move o sensor lidar de acordo com o angulo dado    
        motor_lidar.on_to_position(position=(ANGULO_GIRO_LIDAR*(i+1))-giro_robo,speed=VELOCIDADE_GIRO_LIDAR)
        time.sleep(LIDAR_SLEEP_TIME)
    return distancias



# ------------------------------------------------------- #
# Muda vetores em distancia (cm) para calores cartesianos #
# ------------------------------------------------------- #
def Distancias_Para_Coordenada(distancias, delta_pos, delta_coord):
    y = []
    x = []
    
    # dif_y = 0
    # dif_x = 0
    dif_x = delta_pos[POS_X]-(delta_coord[POS_X]*TAMANHO_GRID_CM)
    dif_y = delta_pos[POS_Y]-(delta_coord[POS_Y]*TAMANHO_GRID_CM)
    
    for i in range(QTD_MEDIDAS_LIDAR):
        # Obtem angulo em graus e converte para radianos
        ang_deg = 90-(ANGULO_GIRO_LIDAR*i) # Graus
        ang_rad = math.radians(ang_deg)    # Radianos
        
        y_ = ((distancias[i]*(math.sin(ang_rad)))-dif_y)
        x_ = ((distancias[i]*(math.cos(ang_rad)))-dif_x)
        
        # Calcula modulos x e y para os vetores de distancia obtidos
        y.append(round(y_/TAMANHO_GRID_CM))
        x.append(round(x_/TAMANHO_GRID_CM)) 
    
    dist = [x,y]
    return dist


# Função que retorna as coordenadas (x,y), no referencial de uma matriz, de um vetor(dx,dy)
# cuja origem é um ponto centr(x,y) qualquer pertencente a esta matriz
def Muda_Referencia(vetor, centro):
    coord = [0,0]
    
    coord[POS_X] = centro[POS_X] + vetor[POS_X]
    coord[POS_Y] = centro[POS_Y] - vetor[POS_Y]
    
    return coord



# Retorna uma matriz valores[2][QTD_VALORES] que indica as coordenadas [x][y]
# de cada ponto visto pelo sensor a aprtir das informações do vetor e da parede
# para qual ele aponta
def Retorna_Espacos_Conhecidos(vetor, wall, ang_v_rad, delta_coord):
    lista = [[],[]]
    num = 0
    
    x = 1 if vetor[POS_X] < 0 else 0
    y = 0
    
    if vetor[POS_X] == 0:
        for _ in range(abs(wall[POS_Y])):
            if vetor[POS_Y] > 0: y += 1
            if vetor[POS_Y] < 0: y -= 1
            
            lista[POS_X].append(x-delta_coord[POS_X])
            lista[POS_Y].append(y-delta_coord[POS_Y])
        return lista
    
    
    while(abs(x)-abs(wall[POS_X]) < 0 or (abs(y)-abs(wall[POS_Y])) < 0) and num < 1000: 
        if vetor[POS_X] > 0: x += 1
        if vetor[POS_X] < 0: x -= 1
      
        y = round(math.tan(ang_v_rad) * x)
        
        lista[POS_X].append(x-delta_coord[POS_X])
        lista[POS_Y].append(y-delta_coord[POS_Y])
        num += 1
    return lista
    


# ---------------------------------------------------- #
# Cria mapa temporário que alterará o valor dos outros #
# ---------------------------------------------------- #
def Cria_Mapa_Distancias(delta_pos, raw_values, delta_coord):
    
    dist = Distancias_Para_Coordenada(raw_values, delta_pos, delta_coord)
    # print("dist =", dist)
    
    x = dist[POS_X]
    y = dist[POS_Y]

    maiores = [max(x),max(y)] # Posicoes limite Leste e Norte
    menores = [min(x),min(y)] # Posições limite Oeste e Sul


    # Iniciliza mapa
    mapa = Mapa()

    # Definindo tamanho do mapa (N,S,L,O) de acordo com o padrão da Classe Mapa()
    # +1 e -1 para considerar as paredes em cada direcao
    mapa.tam[POS_NORTE] = (maiores[POS_Y]+1)    - delta_coord[POS_Y]
    mapa.tam[POS_SUL]   = abs(menores[POS_Y]-1) + delta_coord[POS_Y]
    mapa.tam[POS_LESTE] = (maiores[POS_X]+1)    - delta_coord[POS_X]
    mapa.tam[POS_OESTE] = abs(menores[POS_X]-1) + delta_coord[POS_X]
    
    
    # Tamanho da grid de acordo com leitura
    # +1 para considerar o espaco em que o robo esta
    x_size = int(mapa.tam[POS_LESTE] + mapa.tam[POS_OESTE])+1 # Tamanho horizontal (Leste -> Oeste)
    y_size = int(mapa.tam[POS_NORTE] + mapa.tam[POS_SUL])  +1 # Tamanho vertical   (Norte -> Sul)
    
    # Cria matriz de acordo com tamanho
    # 8 é usado como valor buffer para representar lugares desconhecidos
    mapa.matriz = [[8 for _ in range(x_size)]for _ in range(y_size)] 
    
    # Define coordenadas do ponto de referência/ancoragem na matriz
    mapa.center[POS_X] = mapa.tam[POS_OESTE] 
    mapa.center[POS_Y] = mapa.tam[POS_NORTE] 
    
    
    # Coordenadas para pontos conhecidos da matriz do mapa
    known_xs = [] # Valores x
    known_ys = [] # Valores y
    
    # Coordenadas para pontos das paredes na matriz do mapa
    walls_xs = [] # Valores x
    walls_ys = [] # Valores y
    
    
    for i in range(QTD_MEDIDAS_LIDAR):
        # Obtem angulo em graus e converte para radianos
        ang_deg = 90-(ANGULO_GIRO_LIDAR*i) # Graus
        ang_rad = math.radians(ang_deg)    # Radianos
        

        if x[i] == 0: val_x = 0
        if x[i] >  0 or round(math.cos(ang_rad)+0.35) >=  1: val_x =  1
        if x[i] <  0 or round(math.cos(ang_rad)-0.35) <= -1: val_x = -1
        
        if y[i] == 0: val_y = 0
        if y[i] >  0 or round(math.sin(ang_rad)+0.35) >=  1: val_y =  1
        if y[i] <  0 or round(math.sin(ang_rad)-0.35) <= -1: val_y = -1
        
        # Marca parede como espaço para qual o vetor aponta
        wall_x = x[i]+val_x
        wall_y = y[i]+val_y
        
        # walls.append(Muda_Referencia([wall_x,wall_y], mapa.center))
        wall = Muda_Referencia([wall_x,wall_y], mapa.center)
        
        walls_xs.append(wall[POS_X]-delta_coord[POS_X])
        walls_ys.append(wall[POS_Y]+delta_coord[POS_Y])
        
        known_ = (Retorna_Espacos_Conhecidos([x[i],y[i]], [wall_x,wall_y], ang_rad, delta_coord))
        
        for j in range(len(known_[POS_X])):
            known_xs.append(known_[POS_X][j])
            known_ys.append(known_[POS_Y][j])
        
    
    # Marca pontos conhecidos (MISS) como 0
    for i in range(len(known_xs)):
        [known_xs[i], known_ys[i]] = Muda_Referencia([known_xs[i],  known_ys[i]], mapa.center)
        if known_ys[i] in range(y_size) and known_xs[i] in range(x_size):
            mapa.matriz[int(known_ys[i])][int(known_xs[i])] = 0
    
    # Marca pontos conhecidos (HIT) como 1
    for i in range(len(walls_xs)):
        if walls_ys[i] in range(y_size) and walls_xs[i] in range(x_size):
            mapa.matriz[walls_ys[i]][walls_xs[i]] = 1
    
    # # # Marca posicao do robo na grid
    # mapa.matriz[mapa.tam[POS_NORTE]][mapa.tam[POS_OESTE]] = 3
    # mapa.matriz[mapa.center[POS_Y]][mapa.center[POS_X]] = 2

    return mapa


# --------------------------------------- #
# Copia os itens de uma matriz para outra #
# --------------------------------------- #
def M_cpy(matriz):
    cpy = []    
    
    for line in matriz:
        cpy.append(line)
    return cpy



# ----------------------------------------------------------------------------------- #
# Encontra o caminho de orgem(x,y) até destino(x,y) a partir de um mapa de distancias #
# ----------------------------------------------------------------------------------- #
def encontrarCaminho(mapaDist, origemX,origemY,destinoX,destinoY,size_x,size_y):
    direcoes = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    caminho_ = []
    caminho = []
    x,y = origemX,origemY # x,y iniciais do robô
    num = 0
    
    while ((x,y) != (destinoX,destinoY)): # Enquanto o robô não estiver no lugar, não para
        caminho_.append((x,y))
        for (dx,dy) in direcoes:
            nx,ny = x + dx, y + dy

            # Verifica se o quadrado adjacente possui um número menor que o atual
            if (0 <= nx < size_x) and (0 <= ny < size_y) and (mapaDist[ny][nx] < mapaDist[y][x]) and (mapaDist[ny][nx] != -1):
                x, y = nx, ny
                break
        num += 1
        
    caminho_.append((destinoX, destinoY)) # Adiciona a coordenada [0,0]
    
    for i in reversed(caminho_):
        caminho.append(i)
    return caminho



# Caminho_Prox_Desconhecido(hits, unknown, delta_coord_atual)
def Caminho_Prox_Desconhecido(mapa_paredes, mapa_desconhecidos, delta_coord):
    # Marca ponto de partida do robo dentro da matriz
    pos_robo = [mapa_paredes.center[POS_X]-delta_coord[POS_X], mapa_paredes.center[POS_Y]+delta_coord[POS_Y]]

    dist = Mapa()
    dist.center = mapa_paredes.center
    dist.tam    = mapa_paredes.tam
    
    size_x = int(dist.tam[POS_LESTE] + dist.tam[POS_OESTE])+1
    size_y = int(dist.tam[POS_NORTE] + dist.tam[POS_SUL])  +1
    
    dist.matriz = [[-1 for _ in range(size_x)] for _ in range(size_y)]
    
    # Ponto de inicio recebe distancia 0
    dist.matriz[pos_robo[POS_Y]][pos_robo[POS_X]] = 0 
    
    encontrado = False
    delta = 0
    
    # Matriz [QTD_VALORES][2] que indica ultimos pontos marcados
    last_marked = [pos_robo]
    new_last_m  = []
    coord_dest = [pos_robo[POS_X], pos_robo[POS_Y]]
    
    while(encontrado == False):
        delta += 1
        # Para cada ponto marcado recentemente
        for p in last_marked:
            # print("p =", p)
            if p[POS_Y] > 0:
                if dist.matriz[p[POS_Y] - 1][p[POS_X]] == -1 and mapa_paredes.matriz[p[POS_Y] - 1][p[POS_X]] < 1:
                    dist.matriz[p[POS_Y] - 1][p[POS_X]] = delta
                    if mapa_desconhecidos.matriz[p[POS_Y] - 1][p[POS_X]] > 0: 
                        coord_dest = [p[POS_X], p[POS_Y] - 1+1]
                        encontrado = True
                        break 
                    new_last_m.append([p[POS_X], p[POS_Y] - 1])
            
            if p[POS_Y] < size_y-1:
                if dist.matriz[p[POS_Y] + 1][p[POS_X]] == -1 and mapa_paredes.matriz[p[POS_Y] + 1][p[POS_X]]  < 1:
                    dist.matriz[p[POS_Y] + 1][p[POS_X]] = delta
                    if mapa_desconhecidos.matriz[p[POS_Y] + 1][p[POS_X]] > 0: 
                        coord_dest = [p[POS_X], p[POS_Y] + 1-1]
                        encontrado = True
                        break 
                    new_last_m.append([p[POS_X], p[POS_Y] + 1])
            
            if p[POS_X] < size_x-1:
                if dist.matriz[p[POS_Y]][p[POS_X] + 1] == -1 and mapa_paredes.matriz[p[POS_Y]][p[POS_X] + 1] < 1:
                    dist.matriz[p[POS_Y]][p[POS_X] + 1] = delta
                    if mapa_desconhecidos.matriz[p[POS_Y]][p[POS_X] + 1] > 0: 
                        coord_dest = [p[POS_X] + 1-1, p[POS_Y]]
                        encontrado = True
                        break 
                    new_last_m.append([p[POS_X] + 1, p[POS_Y]])
            
            if p[POS_X] > 0:
                if dist.matriz[p[POS_Y]][p[POS_X] - 1] == -1 and mapa_paredes.matriz[p[POS_Y]][p[POS_X] - 1] < 1:
                    dist.matriz[p[POS_Y]][p[POS_X] - 1] = delta
                    if mapa_desconhecidos.matriz[p[POS_Y]][p[POS_X] - 1] > 0: 
                        coord_dest = [p[POS_X] - 1+1, p[POS_Y]]
                        encontrado = True
                        break 
                    new_last_m.append([p[POS_X] - 1, p[POS_Y]])
        
        
        # print("new_last_m =", new_last_m)
        last_marked = M_cpy(new_last_m)
        new_last_m = []
        
        # print("last_marked =", last_marked)
        if last_marked == [] and encontrado != True:
            return None
    
    print("dist=")
    print(dist)
    time.sleep(1)
        
    print("origem =", pos_robo)
    print("destino =", coord_dest)
        
    caminho = encontrarCaminho(dist.matriz, coord_dest[POS_X], coord_dest[POS_Y], pos_robo[POS_X], pos_robo[POS_Y],size_x,size_y)

    print("Caminho =", caminho)
    return caminho




#=========================#
#                         #
#  ~~~ Loop Principal ~~~ #
#                         #
#=========================#
while True:
    print("="*50+"\n\n")
    
    # Posicioes atuais do robo em relacao ao ponto inicial em centimetros e em coordenadas
    delta_pos_atual   = [P_INICIAL[POS_X]-sensor_gps.x, P_INICIAL[POS_Y]-sensor_gps.y]
    delta_coord_atual = [round(delta_pos_atual[POS_X]/TAMANHO_GRID_CM), round(delta_pos_atual[POS_Y]/TAMANHO_GRID_CM)]
    
    # Obtem angulo atual de giro do robô
    angulo = sensor_giro.angle 
    
    print("posicao =", delta_pos_atual)
    print("delta_coord_atual =", delta_coord_atual)
    print("angulo  =", angulo)
    
    # Obtem uma serie de medidas e seu mapa
    medidas = Obtem_Distancias(angulo)
    
    print("medidas =", medidas)
    
    mapa_1 = Cria_Mapa_Distancias(delta_pos_atual, medidas, delta_coord_atual)
    
    hits.atualiza(mapa_1, "hit", delta_coord_atual)
    miss.atualiza(mapa_1, "miss", delta_coord_atual)
    unknown.atualiza(mapa_1, "unknown", delta_coord_atual)
    
    print("mapa 1 =")
    print(mapa_1)
    time.sleep(0.3)
    
    print("hit =")
    print(hits)
    time.sleep(0.3)
    
    print("miss =")
    print(miss)
    time.sleep(0.3)
    
    print("desconhecidos =")
    print(unknown)
    time.sleep(0.3)
    
    movimento = Caminho_Prox_Desconhecido(hits, unknown, delta_coord_atual)
    
    if movimento != None:
        Movimento_Robo(movimento, TAMANHO_GRID_CM, TAMANHO_GRID_CM)
        print("Movimento concluido!")
        time.sleep(0.5)
        
    else:
        print("Mapeamento concluido!")
        mapa_final = Mapa()
        mapa_final.Mapa_Final(hits, miss, unknown)
        
        print("Mapa final =")
        print(mapa_final)
        time.sleep(3600)
    
    mapa_final = Mapa()
    mapa_final.Mapa_Final(hits, miss, unknown)
        
    print("Mapa final =")
    print(mapa_final)
