import numpy as np
from collections import deque

# Propagação da onda
def propagaOnda(mapa, destino_x, destino_y):
  linhas, colunas = len(mapa), len(mapa[0])
  distancia = mapa
  for i in range(12):
    for j in range(10):
      if distancia[i][j] == 0:
        distancia[i][j] = 1000
  distancia[destino_x][destino_y] = 0
  fila = deque([(destino_x, destino_y)])
  
  # Direções: cima, baixo, esquerda, direita
  direcoes = [(-1, 0), (1, 0), (0, -1), (0, 1)]

  while fila:
    x, y = fila.popleft() # Pega as coordenadas na fila
    for dx, dy in direcoes:
      nx, ny = x + dx, y + dy  # Soma as direções às coordenadas atuais
      if 0 <= nx < linhas and 0 <= ny < colunas and mapa[nx][ny] != 1:  # Se tá dentro do range da matriz e não é obstáculo
        if distancia[nx][ny] > distancia[x][y] + 1:
          distancia[nx][ny] = distancia[x][y] + 1  # Substitui o valor de uma coordenada pelo seu sucessor caso a distância das casas seja menor que a atual
          fila.append((nx, ny)) # Acrescenta ao final o novo par de coordenadas

mapa = [[0 for _ in range(colunas)] for _ in range(linhas)]

mapa[3][0] = -1
mapa[3][1] = -1
mapa[3][2] = -1
mapa[3][3] = -1
mapa[3][4] = -1
mapa[3][5] = -1
mapa[3][6] = -1

mapa[8][7] = -1
mapa[8][8] = -1
mapa[9][7] = -1
mapa[9][8] = -1

waveFront(mapa,0,0)
  
  

  
    
