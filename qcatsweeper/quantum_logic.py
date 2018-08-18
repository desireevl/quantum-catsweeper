from qiskit import QuantumProgram
from enum import Enum
from qcatsweeper import qconfig

import math
import random
import quantumrandom as qr


class TileItems(Enum):
    BLANKS = 0
    GROUP1 = 1
    GROUP2 = -1
    GROUP3 = 2
    GROUP4 = -2
    GROUP5 = 3
    GROUP6 = -3
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

def new_game_grid(l, bomb_no=20):
    game_grid = [[TileItems.BLANKS for i in range(l)] for j in range(l)]

    # Construct groups of numbers
    _cur = 0
    _index = [TileItems.GROUP1, TileItems.GROUP2, TileItems.GROUP3,
              TileItems.GROUP4, TileItems.GROUP5, TileItems.GROUP6]
    random.shuffle(_index)
    _groups = [[random.randint(0, 1) for i in range(l)] for i in range(l)]
    
    for y in range(0, l, 4):
        for x in range(0, l, 6):            
            for _y in range(y, y+4):
                for _x in range(x, x+6):                    
                    if _groups[_y][_x] >= 1:
                        game_grid[_y][_x] = _index[_cur]
            _cur += 1

    # 20 bombs
    # bomb_xy = qr.get_data(data_type='uint16', array_length=bomb_no * 2)
    # bomb_xy = list(map(lambda x: x % l, bomb_xy))
    bomb_xy = [random.randint(0, l-1) for i in range(bomb_no * 2)]
    bomb_xy = [bomb_xy[i:i+2] for i in range(0, bomb_no * 2, 2)]

    for coord in bomb_xy:
        if len(coord) > 0:
            game_grid[coord[0]][coord[1]] = TileItems.BOMB_UNEXPLODED

    return game_grid


def onclick(clicked_tile, num_clicks):
    """
    params:
    clicked_tile: tile type of the clicked tile
    num_click: number of times a group has been clicked
    """
    print(clicked_tile, num_clicks)

    if (clicked_tile == TileItems.BOMB_UNEXPLODED):
        gridScript.h(q[0])
        gridScript.measure(q[0], c[0])
        results = Q_program.execute(
            ["gridScript"], backend=device, shots=shots, timeout=1800)
        re = results.get_counts("gridScript")

        d1 = list(map(lambda x: (x[0], x[1], x[0].count('0')), re.items()))
        d2 = sorted(d1, key=lambda x: x[2], reverse=True)
        if d2[0][2] > d2[1][2]:
            return TileItems.BOMB_EXPLODED
        else:
            return TileItems.BLANKS

    elif (clicked_tile == TileItems.GROUP1 or clicked_tile == TileItems.GROUP2): # 1 click
        gridScript.x(q[1])
        gridScript.measure(q[1], c[1])
        results = Q_program.execute(
            ["gridScript"], backend=device, shots=shots, timeout=1800)
        re = results.get_counts("gridScript")

        # is occurence for '00000' > '00001' or the other way
        if len(re) > 1:
            d1 = list(map(lambda x: (x[0], x[1], x[0].count('0')), re.items()))
            d2 = sorted(d1, key=lambda x: x[2], reverse=True)            
            if d2[0][2] > d2[1][2]:
                return TileItems.REVEAL_GROUP
            val = list(re.keys())[0]
            if val.count('1') > val.count('0'):
                return TileItems.REVEAL_GROUP
            return None
                
    elif (clicked_tile == TileItems.GROUP3 or clicked_tile == TileItems.GROUP4): # 2 clicks
        if num_clicks == 1:
            gridScript.u3(0.5 * math.pi, 0.0, 0.0, q[2])
            return None
        elif num_clicks == 2:
                gridScript.u3(0.5 * math.pi, 0.0, 0.0, q[2])
                gridScript.u3(0.5 * math.pi, 0.0, 0.0, q[2])
                return TileItems.REVEAL_GROUP

    elif (clicked_tile == TileItems.GROUP5 or clicked_tile ==TileItems.GROUP6): # 3 clicks
        if num_clicks == 1:
            gridScript.u3(1/3 * math.pi, 0.0, 0.0, q[3])
            return None
        elif num_clicks == 2:
            gridScript.u3(1/3 * math.pi, 0.0, 0.0, q[3])
            gridScript.u3(1/3 * math.pi, 0.0, 0.0, q[3])
            return None
        elif num_clicks == 3:
            gridScript.u3(1/3 * math.pi, 0.0, 0.0, q[3])
            gridScript.u3(1/3 * math.pi, 0.0, 0.0, q[3])
            gridScript.u3(1/3 * math.pi, 0.0, 0.0, q[3])
            return TileItems.REVEAL_GROUP


