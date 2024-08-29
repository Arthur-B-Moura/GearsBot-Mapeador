import numpy as np
from collections import deque

# Constantes
COORD_DESTINO = np.array([xDest,yDest)]
COORD_ROBO = np.array([xRobo,yRobo)]
mapa = matrizMapa

# Variáveis
coordAtual = COORD_DESTINO

# Propagação da onda
def propagaOnda():
  # Direções: cima, baixo, esquerda, direita
  direcoes = [(-1, 0), (1, 0), (0, -1), (0, 1)]

  while fila:
    x, y = fila.popleft() # Pega as coor
    for dx, dy in direcoes:
      nx, ny = x + dx, y + dy
      if 0 <= nx < linhas and 0 <= ny < colunas and mapa[nx][ny] != 1:
        if distancia[nx][ny] > distancia[x][y] + 1:
          distancia[nx][ny] = distancia[x][y] + 1
          fila.append((nx, ny))

  
  
  

  
    
