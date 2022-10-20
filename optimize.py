# Author: Jacob Dawson
#
# This function will attempt to optimize for the best-performing
# (read: highest gain) antenna, as determines by the fitness
# function defined in the file fitness.py.
#
# To get started, we'll try to make a function which optimizes
# using scipy's optimization algorithms. Please note that none
# of these algs are evolutionary, to my knowledge--instead, they're
# all different hill-climbers and stuff like that. Nevertheless,
# should be a useful proof of concept if I eventually want to take
# the evolutionary approach!

from fitness import *
import scipy

def optimize():
    # we'll compare our results against a monopole that I hand-design
    # for the purpose of receiving 137 MHz
    baseAntenna = [(0.0,0.0,0.52)] # z is up!
    # a 52 cm monopole receives 137 MHz, but not well with
    # right-hand-polarized signal, so that's why we need this
    # optimization algorithm!
    print(f"Hand-designed antenna has a gain of {fitness(frequency=137,polarizationType='RHP',wires=baseAntenna)}")

    # okay... now how does scipy's optimizer work?

if __name__=='__main__':
    optimize()
