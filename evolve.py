# Author: Jacob Dawson
#
# This function will attempt to optimize for the best-performing (read:
# highest gain for some scenario) antenna, as determined by the fitness
# function defined in the file fitness.py.
#
# As it turns out, scipy has a lot of different in-library options
# for optimization, including (!) an evolutionary algorithm called
# "differential_evolution". Not entirely sure what differential means
# here, but this code is a million times better than what I could
# have done, so that's a win!

from fitness import *
#from scipy.optimize import minimize
#from scipy.optimize import basinhopping
from scipy.optimize import differential_evolution

def optimize(num_wires=5):
    # we'll compare our results against a monopole that I hand-design
    # for a given purpose. An easy rule of thumb is to make a quarter-wave
    # dipole. I use this calculator to find the vertical height:
    # m0ukd.com/calculators/quarter-wave-ground-plane-antenna-calculator/
    baseAntenna = [0.0,0.0,0.178, 0.0,0.0,0.356] # z is up! Also, there are two parts here because c3cpp can't do single-wire antennas for some reason
    baseAntennaGain = fitness(wiresInput=baseAntenna)
    print(f"Hand-designed antenna has a fitness of {-baseAntennaGain}")
    _, _, mean_gain, max_gain, min_gain = processAntenna(baseAntenna)
    print(f"mean:{mean_gain}\nmax:{max_gain}\nmin:{min_gain}")

    # okay... now how does scipy's optimizer work?
    # res = minimize(fun = simple_poly, x0 = 20)
    # ^ is an example of working optimize() code, where fun() is just
    # a minimizable lambda function (a parabola or something)

    # First idea: simply minimize. As it turns out, this might not be great
    # because I don't think it does "random restarts".
    '''results = minimize(
        fun = fitness,
        #x0 = [0.0,0.0,0.13, 0.0,0.0,0.26, 0.0,0.0,0.39, 0.0,0.0,0.52],
        #x0 = [0.0,0.0,0.26, 0.0,0.0,0.52],
        #x0 = [0.0,0.0,0.1733, 0.0,0.0,0.3467, 0.0,0.0,0.52],
        #x0 = [0.01,0.02,0.03, 0.04,0.05,0.06, 0.07,0.08,0.09, 0.15,0.2,0.3, 1,2,3],
        x0 = [0.01,0.02,0.03, 0.04,0.05,0.06, 0.07,0.08,0.09, 0.15,0.2,0.3],
        options = {
            "disp": True,
            "maxiter": 10
        }
    )'''

    # Second option: this appears to work better, because x0 is just the
    # first "guess", from which it hops around, locally minimizes those
    # hops, and then proceeds, hopefully finding a global optimum. Takes a
    # while though--is there a way to multithread?
    '''
    results = basinhopping(
        func = fitness,
        x0 = [0.0,0.0,0.1, 0.0,0.0,0.35, 0.0,0.0,0.7],
        interval=10,
        niter=10,
    )
    '''

    # this... is exactly what I was looking for. This code, optimized by scipy,
    # uses all cores to find a global minimum using an evolutionary algorithm,
    # WITHOUT an initial guess!
    results = differential_evolution(
        func = fitness,
        bounds = [(-0.5,0.5), (-0.5,0.5), (0.001,0.5),] * num_wires,
        # modify these ^ dimensions to specify the bounds on antenna shape!
        popsize = 50,
        maxiter = 100,
        seed = 3,
        workers = -1,
        disp = True,
        updating = "deferred",
        polish = False,
        mutation = (0.25, 1.75),
        recombination = 0.9,
    )
    print("best antenna:",results)
    _, wireLength, mean_gain, max_gain, min_gain = processAntenna(results.x)
    print(f"mean:{mean_gain}\nmax:{max_gain}\nmin:{min_gain}\ntotal wire length:{wireLength}")
    return results.x


if __name__=='__main__':
    x = optimize(num_wires=3)
    print(x)
