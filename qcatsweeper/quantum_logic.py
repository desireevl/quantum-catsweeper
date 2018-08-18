from qiskit import QuantumProgram
from enum import Enum
from qcatsweeper import qconfig

import math
import qconfig
import random
import quantumrandom as qr


class TileItems(Enum):
    UNCLICKED = -2
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
    REVEAL_GROUP = 9

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


# for row in game:
#     print(row)


def new_game_grid(l, bomb_no=20):
    game_grid = [[TileItems.BLANKS for i in range(l)] for j in range(l)]

    # 20 bombs
    bomb_xy = qr.get_data(data_type='uint16', array_length=bomb_no)
    bomb_xy = list(map(lambda x: x % l, bomb_xy))
    bomb_xy = [bomb_xy[i:i+2] for i in range(0, math.ceil(bomb_no/2), 2)]

    for coord in bomb_xy:
        if len(coord) > 0:
            game_grid[coord[0]][coord[1]] = TileItems.BOMB_UNEXPLODED

    return game_grid


def onclick( clicked_tile, num_click):
    """
    params:
    clicked_tile: tile type of the clicked tile
    num_click: number of times a group has been clicked
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

    elif (clicked_tile == TileItems.GROUP1 and clicked_title == TileItems.GROUP2): # 1 click
        gridScript.x(q[1])
        gridScript.measure(q[1], c[1])
        results = Q_program.execute(["gridScript"], backend=device, shots=shots, wait=5, timeout=1800)
        re = results.get_counts("gridScript")

        if len(re) > 1:
            d1 = list(map(lambda x: (x[0], x[1], x[0].count('0')), re.items()))
            d2 = sorted(d1, key=lambda x: x[2], reverse=True)
            if d2[0][2] > d2[1][2]:
                return TileItems.REVEAL_GROUP
            else:
                val = list(re.keys())[0]
                if val.count('1') > val.count('0'):
                    return TileItems.REVEAL_GROUP


    elif (clicked_tile == TileItems.GROUP3 and clicked_title == TileItems.GROUP4)): # 2 clicks
        if num_clicks == 0:
            gridScript.u3(0.5 * math.pi, 0.0, 0.0, q[2])
            return TileItems.CLICKED
        elif num_clicks == 1:
                gridScript.u3(0.5 * math.pi, 0.0, 0.0, q[2])
                gridScript.u3(0.5 * math.pi, 0.0, 0.0, q[2])
                return TileItems.REVEAL_GROUP


    # elif (clicked_tile == TileItems.GROUP5 and clicked_title ==TileItems.GROUP6): # 3 clicks

