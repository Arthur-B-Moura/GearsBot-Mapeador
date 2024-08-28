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
        self.matriz = [0]
        self.center = [0,0]
        self.tam    = [0,0,0,0]

    def __str__(self) -> str:
        return self.matriz
    
    def atualiza(self, mapa_opc, map_type):
        new_m = Mapa()

        new_m.tam = [max(n) for n in zip(self.tam, mapa_opc.tam)] # Tamanho da matriz resultante
    
#       centro_x = size_x - Leste - 1
#       centro_y = size_y - Norte 
        size_x = len(new_m.matriz[0])
        size_y =  len(new_m.matriz)
        
        new_m.center[POS_X] = size_x - new_m.tam[POS_LESTE] - 1
        new_m.center[POS_Y] = size_y - new_m.tam[POS_NORTE] - 1

        # for i in range(size_y):
        #     for j in range(size_x):
        #         new_m.matriz[i][j] = self.matriz[i][j] + 1 if mapa_opc.matriz[i][j] == 1

hits = Mapa()
att1 = Mapa()
att2 = Mapa()