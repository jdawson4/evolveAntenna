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
from scipy.optimize import minimize

def optimize():
    # we'll compare our results against a monopole that I hand-design
    # for the purpose of receiving 137 MHz
    baseAntenna = [0.0,0.0,0.52] # z is up!
    # a 52 cm monopole receives 137 MHz, but not well with
    # right-hand-polarized signal, so that's why we need this
    # optimization algorithm!
    #baseAntennaGain = fitness(frequency=137,polarizationType='RHP',wires=baseAntenna)
    baseAntennaGain = fitness(wiresInput=baseAntenna)
    print(f"Hand-designed antenna has a gain of {-baseAntennaGain}")

    # okay... now how does scipy's optimizer work?
    # res = minimize(fun = simple_poly, x0 = 20)
    # ^ is an example of working optimize() code

    # soooo....
    results = minimize(
        fun = fitness,
        #x0 = [0.0,0.0,0.13, 0.0,0.0,0.26, 0.0,0.0,0.39, 0.0,0.0,0.52],
        #x0 = [0.0,0.0,0.26, 0.0,0.0,0.52],
        #x0 = [0.0,0.0,0.1733, 0.0,0.0,0.3467, 0.0,0.0,0.52],
        x0 = [0.1,0.2,0.3, 0.4,0.5,0.6, 0.7,0.8,0.9],
        options = {
            "disp": True,
            "maxiter": 10
        }
    )
    print(results)
    return results.x


if __name__=='__main__':
    optimize()
