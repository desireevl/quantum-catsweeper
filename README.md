# Quantum Cat-sweeper

This is a super simple game loosely based on Minesweeper Flags and runs on the [IBM Quantum computer](https://quantumexperience.ng.bluemix.net/qx/experience) or simulator. 

# Rules of the game:
- Don't explode the cat (bombs)
- The tile numbers indicate the number of times you need to click on the same colour to reveal the whole group
- If a tile has an ! at the end that means quantum probability was not in your favour and that tile click does not count
- To win the game, find the golden kitty (who moves based on whether you reveal a ! or normal tile)

![Front Screen](https://github.com/desireevl/quantum-catsweeper/blob/master/images/mainscreen.PNG)

## Game Page
![Game Screen](https://github.com/desireevl/quantum-catsweeper/blob/master/images/playin.PNG)

## Game Over
![Game Over](https://github.com/desireevl/quantum-catsweeper/blob/master/images/lost.png)

# Explanation
The placement of the bombs are determined using the [ANU Quantum Random Number Generator](https://qrng.anu.edu.au/). A Hadamard gate is used on the qubit that represents the bomb and when the tile is clicked, the qubit is measured. It has a 50/50 chance of evaluating to a 1 (bomb explodes) or a 0 (bomb defuses).

A half NOT gate is applied to each qubit representing a number tile. For example: if you reveal a purple 3 tile, you need to click two more purple 3 tiles before the whole purple section reveals. For each click there is a 50/50 chance of the qubit evaluating to a 1 or 0. If out of the 1024 shots, more of them are 1, then your click counts and you only need to find one more purple tile before the whole group reveals. If there are more 0's, then your click does not count and you still need two more clicks of a purple tile to reveal the group. 

The golden cat moves around based on your click. If you find it you win 100% of the time. If you reveal a tile with a positive (not !) or neutral evaluation (defused bombs, blank tiles) then the cat moves one space in the direction of the tile you just clicked. If a negatively evaluated tile is clicked the golden cat moves one space away. This knowledge can be used as strategy to win the game. 

# Installation Guide
```bash
apt-get install python3 python3-pip libglfw3 libportaudio2 libasound-dev

pip install -r requirements.txt

python main.py
python main.py debug # For debugging mode
```
