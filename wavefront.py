from collections import deque

# Constantes
COORD_DESTINO = [0,0]
COORD_ROBO = [5,4]

# Relacionados ao mapa
mapa = [[0 for _ in range(10)] for _ in range(12)]
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

direcoes = [(-1, 0), (1, 0), (0, -1), (0, 1)]
linhas, colunas = len(mapa), len(mapa[0])

# Propagação da onda
def propagaOnda(mapa, destinoX, destinoY):
  distancia = mapa
  for i in range(12):
    for j in range(10):
      if distancia[i][j] == 0:
        distancia[i][j] = 1000

  distancia[destinoX][destinoY] = 0
  fila = deque([(destinoX, destinoY)])

  while fila:
    x, y = fila.popleft() # Pega as coordenadas na fila
    for dx, dy in direcoes:
      nx, ny = x + dx, y + dy  # Soma as direções às coordenadas atuais
      if 0 <= nx < linhas and 0 <= ny < colunas and mapa[nx][ny] != 1:  # Se tá dentro do range da matriz e não é obstáculo
        if distancia[nx][ny] > distancia[x][y] + 1:
          distancia[nx][ny] = distancia[x][y] + 1  # Substitui o valor de uma coordenada pelo seu sucessor caso a distância das casas seja menor que a atual
          fila.append((nx, ny))
    
  return distancia

# Encontra o menor caminho entre a origem e o destino
def encontrarCaminho(mapaDist, origemX,origemY,destinoX,destinoY):
  caminho = []
  x,y = origemX,origemY # x,y iniciais do robô

  while (x,y) != (destinoX,destinoY): # Enquanto o robô não estiver no lugar, não para
    caminho.append((x,y))
    for dx,dy in direcoes:
      nx,ny = x + dx, y + dy

      # Verifica se o quadrado adjacente possui um número menor que o atual
      if 0 <= nx < linhas and 0 <= ny < colunas and mapaDist[nx][ny] < mapaDist[x][y] and mapaDist[nx][ny] != -1:
        x, y = nx, ny
        break

  caminho.append((destinoX, destinoY)) # Adiciona a coordenada [0,0]

  return caminho

def printar(string, data):
  print("-"*50)
  print(string)

  for line in data:
    print(line)

  print("-"*50)
  print("")


def waveFront():
  valoresMapa = propagaOnda(mapa,COORD_DESTINO[0], COORD_DESTINO[1])
  caminho = encontrarCaminho(valoresMapa, COORD_ROBO[0], COORD_ROBO[1], COORD_DESTINO[0], COORD_DESTINO[1])

  printar("Mapa", valoresMapa)

  printar("Caminho", caminho)


waveFront()
