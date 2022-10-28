# Author: Jacob Dawson
# The purpose of this file is to be an all-purpose testing file. not much else to it!

from scipy.optimize import minimize

def simple_poly(x):
    # a simple polynomial, we want to optimize this for its minimum.
    # Because this polynomial is so simple (I'll probably do x^2),
    # I'll see if scipy can find the correct minimum quickly. I'm just
    # doing this to figure out how the minimize function works.
    return x*x

res = minimize(fun = simple_poly, x0 = 20)

print(res)

print(isinstance((1,2), tuple))
