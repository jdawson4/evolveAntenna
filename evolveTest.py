# Author: Jacob Dawson
#
# I intended on writing code for an evolutionary algorithm/the genetic
# algorithm myself, but then I found out that SciPy has done this for
# me... sorta. There's a function called differential_evolution() which is
# some kind of evolutionary algorithm... not sure what differentiation does in
# this context. So I'm going to do some testing with it here!

from fitness import *
from scipy.optimize import differential_evolution

def evolve(num_wires=5):
    results = differential_evolution(
        func = fitness,
        bounds = [(-1.0,1.0), (-1.5,1.0), (0.001,1.0),] * num_wires,
        popsize = 10,
        maxiter = 5,
        seed = 3,
        workers = -1,
        disp = True,
        updating = "deferred",
        polish = False,
    )
    print(results)
    return results.x


if __name__=='__main__':
    evolve(num_wires=5)
