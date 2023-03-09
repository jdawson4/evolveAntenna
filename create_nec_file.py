# Author: Jacob Dawson
#
# Given a list of wire coordinates like this:
"""
[
    -0.08995548, -0.16057963, 0.44024533,
    -0.48341465, -0.30803703,  0.31034775,
    0.44899531, -0.08152924, 0.08007004
]
"""
# We want to create a text file with the extension .nec, which looks like this:
"""
CM --- NEC2 Input File created or edited by xnec2c 4.1.1 ---
CE --- End Comments ---
GW     1     1   0.00000E+00  0.00000E+00  0.00000E+00 -8.99000E-02 -1.60500E-01  4.40200E-01  1.50000E-02
GW     2     1  -8.99000E-02 -1.60500E-01  4.40200E-01 -4.83400E-01 -3.08000E-01  3.10300E-01  5.00000E-03
GW     3     1  -4.83400E-01 -3.08000E-01  3.10300E-01  4.48900E-01 -8.15000E-02  8.00000E-02  5.00000E-03
GE     0     0   0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00
EX     1     1     1      0  4.50000E+01  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00
RP     0   100   100      0  0.00000E+00  0.00000E+00  3.60000E+00  3.60000E+00  0.00000E+00  0.00000E+00
FR     0    11     0      0  1.69214E+03  1.00000E-01  1.69314E+03  0.00000E+00  0.00000E+00  0.00000E+00
NH     0     1     1      1  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00
NE     0    10     1     10 -1.35000E+00  0.00000E+00 -1.35000E+00  3.00000E-01  0.00000E+00  3.00000E-01
EN     0     0     0      0  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00
"""

from shared import *
from decimal import Decimal

# Let's get cracking then!
def generateNecFile(input_wires):

    wires = rephraseWires(input_wires)

    with open('outputAntenna.nec', 'w', encoding="utf-8",) as f:
        f.write("CM --- NEC2 Input File created or edited by xnec2c 4.1.1 ---\n")
        f.write("CE --- End Comments ---\n")
        i=1
        prevLocation = (0.0, 0.0, 0.0)
        for x,y,z in wires:
            # first, figure out what strings to display for the first 3
            # coordinates:
            x1String = '%.5E' % Decimal(prevLocation[0])
            if prevLocation[0] < 0:
                x1String = "  " + x1String
            else:
                x1String = "   " + x1String
            y1String = '%.5E' % Decimal(prevLocation[1])
            if prevLocation[1] < 0:
                y1String = " " + y1String
            else:
                y1String = "  " + y1String
            z1String = '%.5E' % Decimal(prevLocation[2])
            if prevLocation[2] < 0:
                z1String = " " + z1String
            else:
                z1String = "  " + z1String

            # and now the next 3 coordinates:
            x2String = '%.5E' % Decimal(x)
            if x < 0:
                x2String = " " + x2String
            else:
                x2String = "  " + x2String
            y2String = '%.5E' % Decimal(y)
            if y < 0:
                y2String = " " + y2String
            else:
                y2String = "  " + y2String
            z2String = '%.5E' % Decimal(z)
            if z < 0:
                z2String = " " + z2String
            else:
                z2String = "  " + z2String

            # string it all together (get it?)
            restOfString = "     1"+x1String+y1String+z1String+x2String+y2String+z2String+"\n"

            # we actually write the wires here
            f.write(f"GW     {i}"+restOfString)
            
            # after all computation is done, we prep for the next iteration:
            i+=1
            prevLocation = (x,y,z)
        
        # great, so the "wires" section is now working. The rest should be
        # static... except for the frequencies of the incident wave.
        # Otherwise, everything will be the same: no ground plane,
        # waves coming from all directions, etc.

        # no ground plane:
        f.write("GE     0     0   0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00\n")

        # linear excitation, I think:
        f.write("EX     1   360   360     0  0.00000E+00  0.00000E+00  0.00000E+00  1.00000E+00  1.00000E+00  1.00000E+00\n")

        # not sure what this does:
        f.write("RP     0   100   100      0  0.00000E+00  0.00000E+00  3.60000E+00  3.60000E+00  0.00000E+00  0.00000E+00\n")

        # here's the thing we have to calculate. We need the frequency we're
        # targeting, and the number of frequencies around that we want to
        # measure as well.
        #TODO: REWRITE THIS
        freqAsString = '%.5E' % Decimal(targetFrequency)
        f.write(f"FR     0     1     0     0  {freqAsString}  1.00000E+00  {freqAsString}  0.00000E+00  0.00000E+00  0.00000E+00\n")

        # not sure what this does:
        f.write("NH     0     1     1      1  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00\n")

        # not sure what this does:
        f.write("NE     0    10     1     10 -1.35000E+00  0.00000E+00 -1.35000E+00  3.00000E-01  0.00000E+00  3.00000E-01\n")

        # not sure what this does:
        f.write("EN     0     0     0      0  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00")
        # IMPORTANT: NO LINE ENDING ^ HERE!

        # and that's all! We should have a well-formed .nec file now!


if __name__ == "__main__":
    # this is just a demonstration for this file
    generateNecFile(
        [
            (-0.08995548,-0.16057963,0.44024533),
            (-0.48341465,-0.30803703,0.31034775),
            (0.44899531,-0.08152924,0.08007004)
        ]
    )
