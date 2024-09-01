import math

#   0 0 0 0 0   : Mapa  ->  5 x 4 (x,y) 
#   0 0 0 0 0   : Centro(x,y)  -> (1,2)
#   0 2 0 0 0   : Tamanho (N,S,L,O)
#   0 0 0 0 0             (2,1,3,1)
# 
# Portanto...:::: Norte = size_y - centro_y
#               :   Sul = size_y - Norte - 1
#               : Leste = size_x - centro_x -1
#               : Oeste = size_x - Leste - 1
#               ================================
#              centro_x = size_x - Leste - 1
#              centro_y = size_y - Norte 

###################################################

# --- self.matriz ---
#
#      [0][1][2][3]
# [0]   0  0  1  0  : Centro (x,y) = (2,1)
# [1]   1  0  0  1  :    Tam (N,S,L,O)
# [2]   0  0  1  0           (1,1,1,2)
#
# --- opc.matriz ---
#
#      [0][1][2][3]
# [0]   0  1  0  0  : Centro (x,y) = (2,1)
# [1]   1  0  0  1  :    Tam (N,S,L,O)
# [2]   0  0  0  0           (1,3,1,2)
# [3]   0  0  0  0
# [4]   0  1  0  0
#
# --- resultante.matriz --- (HIT)
#
#      [0][1][2][3]  : Centro (x,y) = (2,1)
# [0]   0  1  1  0
# [1]   2  0  0  2
# [2]   0  0  1  0
# [3]   0  0  0  0
# [4]   0  1  0  0
#

POS_X = 0
POS_Y = 1

POS_NORTE = 0
POS_SUL   = 1
POS_LESTE = 2
POS_OESTE = 3

class Mapa:
    matriz = [[],[]]
    center = []
    tam = []

    def __init__(self) -> None:
        self.matriz = [[0],[0]]
        self.center = [0,0]
        self.tam    = [0,0,0,0]

    def __str__(self) -> str:
        str = ""
        for line in self.matriz:
            str += f"{line}" + "\n"

        return str
    
    def atualiza(self, mapa_opc, map_type: str) -> None:
        new_m = Mapa() # Inicializa mapa resultante
        
        # Tamanhos cardinais do mapa resultante
        new_m.tam = [max(n) for n in zip(self.tam, mapa_opc.tam)] 
    
        # Marca tamanhos x e y da matriz do mapa resultante
        size_x = int(new_m.tam[POS_LESTE]+new_m.tam[POS_OESTE]) + 1
        size_y = int(new_m.tam[POS_NORTE]+new_m.tam[POS_SUL])   + 1

        # Inicializa matriz do mapa com 0 para cada posição
        new_m.matriz = [[0 for _ in range(size_x)] for _ in range(size_y)]

        # Obtem coordenadas do centro (posição inicial do robô) para o novo mapa
        new_m.center[POS_X] = new_m.tam[POS_OESTE]
        new_m.center[POS_Y] = new_m.tam[POS_NORTE]

        # new_m.center[POS_X] = size_x - new_m.tam[POS_LESTE] - 1
        # new_m.center[POS_Y] = size_y - new_m.tam[POS_NORTE] - 1 # TODO: double check this line later


        # Diferenças de tamanho entre as matrizes 
        # Diferenças de tamanho da matriz self entre a matriz resultante
        d_tam = [new_m.tam[i]-self.tam[i] for i in range(len(self.tam))]
        # if d_tam[POS_OESTE] > 0: d_tam[POS_OESTE] += 1

        # Diferenças de tamanho da matriz opc entre a matriz resultante
        d_tam_opc = [new_m.tam[i]-mapa_opc.tam[i] for i in range(len(mapa_opc.tam))]
        # if d_tam_opc[POS_OESTE] > 0: d_tam_opc[POS_OESTE] += 1

        
        # Valores na matriz resultante
        for i in range(size_y):
            for j in range(size_x):

                i_opc = i - (new_m.tam[POS_NORTE]-mapa_opc.tam[POS_NORTE]) 
                j_opc = j - (new_m.tam[POS_OESTE]-mapa_opc.tam[POS_OESTE])
                
                if i_opc in range(mapa_opc.tam[POS_SUL]+mapa_opc.tam[POS_NORTE]+1) and j_opc in range(mapa_opc.tam[POS_OESTE]+mapa_opc.tam[POS_LESTE]+1): 
                   val = 1 if (map_type == "hit" and mapa_opc.matriz[i_opc][j_opc] == 1) or (map_type == "miss" and mapa_opc.matriz[i_opc][j_opc] == 0) else 0
                else: val = 0
                
                i_old = i - (new_m.tam[POS_NORTE]-self.tam[POS_NORTE]) 
                j_old = j - (new_m.tam[POS_OESTE]-self.tam[POS_OESTE]) 


                if i_old in range(self.tam[POS_SUL]+self.tam[POS_NORTE]+1) and j_old in range(self.tam[POS_OESTE]+self.tam[POS_LESTE]+1): 
                    new_m.matriz[i][j] = self.matriz[i_old][j_old] + val 
                else: new_m.matriz[i][j] = val 
                
                # Atualização de posições para mapa de espaços desconhecidos
                if map_type == "unknown":
                    if i_opc in range(mapa_opc.tam[POS_SUL]+mapa_opc.tam[POS_NORTE]+1) and j_opc in range(mapa_opc.tam[POS_OESTE]+mapa_opc.tam[POS_LESTE]+1): 
                        if mapa_opc.matriz[i_opc][j_opc] == 8: new_m.matriz[i][j] = 1
                        if mapa_opc.matriz[i_opc][j_opc] != 8: new_m.matriz[i][j] = 0
                
                
        
        # Atualiza valores da matriz inicial
        self.matriz = new_m.matriz
        self.center = new_m.center
        self.tam    = new_m.tam


# m1 = Mapa()
# m2 = Mapa()

# #             0 1 2 3 4 5 6 7 8 9
# m1.matriz = [[1,1,1,1,0,0,0,1,0,8,8,8], # 0
#              [1,1,1,1,0,0,0,1,0,8,8,8], # 1 
#              [1,1,1,1,0,0,0,1,0,8,8,8], # 2
#              [1,1,1,1,2,0,0,1,0,8,8,8], # 3
#              [1,1,1,1,0,0,0,1,0,8,8,8], # 4
#              [1,1,1,1,0,0,0,1,0,8,8,8], # 5
#              [1,1,1,1,0,0,0,1,0,8,8,8], # 6
#              [1,1,1,1,0,0,0,1,0,8,8,8], # 7
#              [1,1,1,1,0,0,0,1,0,8,8,8], # 8
#              [1,1,1,1,0,0,0,1,0,8,8,8]] # 9

# m1.center = [4,3]
# m1.tam    = [3,6,7,4]

# print("m1 =")
# print(m1)

# m2.atualiza(m1, "hit")

# print("m2 =")
# print(m2)
