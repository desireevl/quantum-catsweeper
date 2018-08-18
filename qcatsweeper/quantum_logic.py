from qiskit import QuantumProgram
from collections import Counter
from enum import Enum

import operator
import qconfig
import random
import quantumrandom as qr


class TileItems(Enum):
    CLICKED = -1
    BLANKS = 0
    GROUP1 = 1
    GROUP2 = 2
    GROUP3 = 3
    GROUP4 = 4
    GROUP5 = 5
    GROUP6 = 6
    BOMB_UNEXPLODED = 7
    BOMB_EXPLODED = 8


# if (x,y.tile == TileItems.BOMB)
# print(int(round(qr.randint(0,20))))

x = [int(round(qr.randint(0,11))) for i in range(20)]
y = [int(round(qr.randint(0,11))) for i in range(20)]

# print(x)
# print(y)

# x = [i for i in range(12)]
# y = [i for i in range(12)]

real_device = False
shots = 1024

device = 'local_qasm_simulator'
if real_device:
    device = 'ibmqx4'

Q_program = QuantumProgram()
Q_program.set_api(qconfig.APItoken, qconfig.config["url"])
q = Q_program.create_quantum_register("q", 5)
c = Q_program.create_classical_register("c", 5)
gridScript = Q_program.create_circuit("gridScript", [q], [c])   

_width = 12
_height = 12
game = [[0 for x in range(_width)] for y in range(_height)]

x_pos = random.randint(1,3)
x_neg = random.randint(1,3)

# for i in range(len(x)):
#     game[x[i]][y[i]] = 7

#     for ii in range(x_pos):
#         game[x[i]+ii+1][]

# for how many numbers to be placed around
# rand_num2 = [int(round(qr.randint(1,4))) for i in range(20)]
# print(rand_num2)


for row in game:
    print(row)

gridScript.h(q[0])
gridScript.measure(q[0], c[0])
results = Q_program.execute(["gridScript"], backend=device, shots=shots, wait=5, timeout=1800)
re = results.get_counts("gridScript")   

print(re)

d1 = list(map(lambda x: (x[0], x[1], x[0].count('0')), re.items()))
d2 = sorted(d1, key=lambda x: x[2], reverse=True)
if d2[0][2] > d2[1][2]:
    result = 1
else:
    result = 0

print(result)


def onclick(game, x_pos, y_pos, clicked_tile):
    """
    params:
    game: 2 dimensional list
    x: integer
    y: interger
    clicked_tile: tile type of the clicked tile
    """
    if (clicked_tile == TileItems.BOMB):
        gridScript.h(q[0])
        gridScript.measure(q[0], c[0])
        results = Q_program.execute(["gridScript"], backend=device, shots=shots, wait=5, timeout=1800)
        re = results.get_counts("gridScript")

        d1 = list(map(lambda x: (x[0], x[1], x[0].count('0')), re.items()))
        d2 = sorted(d1, key=lambda x: x[2], reverse=True)
        if d2[0][2] > d2[1][2]:
            return TileItems.BOMB_EXPLODED
        else:
            return TileItems.BLANKS
    elif (clicked_tile == TileItems.)
        # game[x][y] == -3
    # elif (game[x][y] == -2): # already clicked tiles
    #     None
    # elif (game[x][y] == 1): #1
        # gridScript.u3(0.5 * math.pi, 0.5 * math.pi, 0.5 * math.pi, q[1])




    # results = Q_program.execute(["gridScript"], backend=device, shots=shots, wait=5, timeout=1800)

        

# onclick(game, 2, 3)