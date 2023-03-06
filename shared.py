# Author: Jacob Dawson
#
# Stores any constants or shared functions for this repo

def rephraseWires(wiresInput):
    if isinstance(wiresInput[0], tuple):
        wires = wiresInput
    elif isinstance(wiresInput[0], float):
        j = 0
        wires = []
        wiresTemp = []
        for i in wiresInput:
            j+=1
            if ((j%3)==0):
                wiresTemp.append(abs(i)) # ensure that coord 3 is always above 0!
                wires.append(tuple(wiresTemp))
                wiresTemp = []
            else:
                wiresTemp.append(i)
    return wires
