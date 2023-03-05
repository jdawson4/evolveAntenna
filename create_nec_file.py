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

# Let's get cracking then!
def generateNecFile(wires):
    with open('outputAntenna.nec', 'w', encoding="utf-8",) as f:
        f.write("CM --- NEC2 Input File created or edited by xnec2c 4.1.1 ---\n")
        f.write("CE --- End Comments ---")


if __name__ == "__main__":
    # this is just a demonstration for this file
    generateNecFile(
        [
            -0.08995548,-0.16057963,0.44024533,
            -0.48341465,-0.30803703,0.31034775,
            0.44899531,-0.08152924,0.08007004,
        ]
    )
