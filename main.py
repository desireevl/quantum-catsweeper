import qcatsweeper.gui as QGUI
import qcatsweeper.quantum_logic as ql
import sys


debugging = len(sys.argv) > 1
QGUI.QuantumCatsweeperApp(debugging=debugging)

# ql.onclick(ql.TileItems.GROUP2, 1)
