# Código Lucas

from collections import deque
import numpy as np

def wavefront(mapa, origem_x, origem_y, destino_x, destino_y):
    linhas, colunas = len(mapa), len(mapa[0])
    distancia = np.full((linhas, colunas), np.inf)
    distancia[destino_x][destino_y] = 0
    fila = deque([(destino_x, destino_y)])
    
    # Direções: cima, baixo, esquerda, direita
    direcoes = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    print("Passo 1: Inicialização")
    print(f"Mapa original:\n{np.array(mapa)}")
    print(f"Matriz de distâncias inicial:\n{distancia}")
    
    # Propagação da onda
    while fila:
        x, y = fila.popleft()
        for dx, dy in direcoes:
            nx, ny = x + dx, y + dy
            if 0 <= nx < linhas and 0 <= ny < colunas and mapa[nx][ny] != 1:
                if distancia[nx][ny] > distancia[x][y] + 1:
                    distancia[nx][ny] = distancia[x][y] + 1
                    fila.append((nx, ny))
        
        print("\nPasso 2: Propagação da onda")
        print(f"Matriz de distâncias atualizada:\n{distancia}")
    
    # Encontrar o caminho
    caminho = []
    x, y = origem_x, origem_y
    while (x, y) != (destino_x, destino_y):
        caminho.append((x, y))
        for dx, dy in direcoes:
            nx, ny = x + dx, y + dy
            if 0 <= nx < linhas and 0 <= ny < colunas and distancia[nx][ny] < distancia[x][y]:
                x, y = nx, ny
                break
    caminho.append((destino_x, destino_y))
    
    print("\nPasso 3: Encontrar o caminho")
    print(f"Caminho encontrado: {caminho}")
    
    return caminho
