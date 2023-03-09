# Author: Jacob Dawson
#
# The idea of this file is to define a function which determines the "fitness"
# of a given antenna given a set of parameters (frequency, gain, whatever).
# We're going to be using the necpp library for this. This function will be
# what we optimize upon! Not sure how machine-learning our optimiziation will
# get, but we can consider this the "loss" we are minimizing.

import necpp
from shapely.geometry import LineString
from math import sqrt
from shared import *

def handle_nec(result):
    if (result != 0):
        print(necpp.nec_error_message())
        return True
    return False

# some dirty code for computing if two wires intersect:
def linesIntersect(a,b):
    x = LineString(a)
    y = LineString(b)
    return x.crosses(y)

def compute_length(wires):
    sum = 0.0
    previous = (0.0, 0.0, 0.0)
    for x2,y2,z2 in wires:
        x1,y1,z1 = previous
        sum += sqrt(((x1 - x2)**2) + ((y1 - y2)**2) + ((z1 - z2)**2))
        previous = (x2, y2, z2)
    return sum

def processAntenna(wiresInput=[(1, 1, 1), (2, 2, 2)]):
    # I'll make a few notes for frequencies I might wanna receive here:
    # AM radio broadcasts are 540 kHz up to 1700 kHz (1.7 MHz). These are vertically polarized
    # FM radio broadcasts are from 88 MHz to 108 MHz, and should be easy to receive. Probably vertically polarized
    # NOAA (& other) weather satellites transmit 137-138 MHz signals from all directions above the horizon with right-handed polarization.
    # TV transmits linearly polarized (horizontally?) at a few weird frequencies, always from a single source (directionality matters). I'll try and list them here (all US):
    #   VHF low is between 54 and 88 MHz
    #   VHF high is between 174 and 216 MHz
    #   UHF is between 470 and 700 Mhz (seems a little unclear what the upper bound is?)
    # ADS-B (for airplane tracking) is vertically polarized at 1090 MHz
    # The hydrogen line (aka 21 cm line) is a naturally occuring (unpolarized) signal at 1420.405751768 MHz
    # The GOES satellites broadcast vertically polarized signals. LRIT are at 1.69214 GHz, and HRIT are at 1.6941 GHz, but with much higher bandwidth
    # (higher gain required for higher frequencies because of atmospheric attenuation!)

    # sorta want these as parameters but whatever.
    # options are 'LIN', 'RHC', and 'LHC'
    polarizationType='RHC'

    # given a list of floats, returns a list of tuples of floats.
    # This lets us compute things more better.
    wires = rephraseWires(wiresInput)

    try:
        context = necpp.nec_create()
        previousEnd = (0, 0, 0)
        lines = []
        i=1
        for x2, y2, z2 in wires:
            if z2 <= 0.0:
                #print(999)
                return [], 1.0, -999.0, -999.0, -999.0
                # can't go below ground!
            x1, y1, z1 = previousEnd
            newestLine = ((x1,y1,z1), (x2,y2,z2))
            for line in lines:
                if linesIntersect(newestLine, line):
                    #print(newestLine, line)
                    return [], 1.0, -999.0, -999.0, -999.0
                    # wires can't intersect! Short circuiting is bad!
            lines.append(newestLine)
            handle_nec(necpp.nec_wire(context, i, 1, x1, y1, z1, x2, y2, z2, 0.001, 1, 1))
            previousEnd = (x2, y2, z2)
            i+=1
        if(handle_nec(necpp.nec_geometry_complete(context, 1))): # says that we've now set the antenna geometry
            # sometimes this messes up though, so return our "failure" signature
            return [], 1.0, -999.0, -999.0, -999.0
        handle_nec(necpp.nec_gn_card(context, 1, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)) # defines ground plane as an infinite surface. Much simpler that way.
        handle_nec(necpp.nec_gn_card(context, -1, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)) # defines ground plane as an infinite surface. Much simpler that way.

        # here we define the frequencies we're looking for. The parameters here
        # define a frequency, and then x other frequencies y steps above that
        # base frequency. Important! This defines how broad of a band our
        # antenna works for!
        handle_nec(necpp.nec_fr_card(context, 0, 5, targetFrequency, 0.1))
        
        # Polarization determines A LOT about antenna architecture. We have
        # options for prcessing left-handed, right-handed, and linear
        # polarization.
        # Left- and right-handed are used by satellites, whereas most
        # terrestrial applications are linearly polarized. Natural radio
        # sources tend to be unpolarized, but there are exceptions!
        if polarizationType=='RHC':
            polarization=2
        elif polarizationType=='LHC':
            polarization=3
        elif polarizationType=='':
            polarization=1
        elif polarizationType=='LIN':
            polarization=1
        else:
            polarization=1
        # here's where polarization gets applied
        handle_nec(necpp.nec_ex_card(context, polarization, 1, 2, 0, 0, 0, 0, 10, 10, 0))


        # this is... quite important. It describes the radiation patterns, particularly where they're coming from.
        #handle_nec(necpp.nec_rp_card(context, 0, 10, 10, 0,5,0,0, 0, 0, 18, 36, 0, 0)) # all angles above the ground
        #handle_nec(necpp.nec_rp_card(context, 0, 10, 10, 0,5,0,0, 0, 0, 6, 36, 0, 0)) # all >30 degrees above the ground (satellites)
        #handle_nec(necpp.nec_rp_card(context, 0, 10, 10, 0,5,0,0, 60, 0, 6, 36, 0, 0)) # everywhere less than 30 degrees above ground (terrestrial signals)
        #handle_nec(necpp.nec_rp_card(context, 0, 1, 1, 0,0,0,0, 90, 0, 1, 1, 0, 0)) # terrestrial signals, but from one spot along the horizon
        handle_nec(necpp.nec_rp_card(context, 0, 5, 5, 0,5,0,0, 134.8, 0, 0.1, 0.1, 0, 0)) # points at one point in the sky 45 degrees above the horizon. This happens to be the position of GOES-16 in my area; it is merely a coincidence that this is such a round number.

        # here's the important part:
        mean_gain = necpp.nec_gain_mean(context, 1)
        max_gain = necpp.nec_gain_max(context, 1)
        min_gain = necpp.nec_gain_min(context, 1)
        # MEAN gain in order to make an omnidirectional... but there again it might just maximize a node still?
        # MAX gain to make a directional antenna, but this will likely only evolve for a single frequency
        # MIN gain to make an omnidirectional, but I am concerned this will penalize nulls too much

        necpp.nec_delete(context) # delete now that we have our calculations
    except Exception as e:
        #print(999)
        print(e)
        return [], 1.0, -999.0, -999.0, -999.0
        # if the processing gets fucked up, we just want to make the alg know
        # that that antenna is invalid.
    wireLength = compute_length(wires)
    return wires, wireLength, mean_gain, max_gain, min_gain
    # we return gain negated, so that our model can *minimize* the negative
    # gain (that is, maximize the gain.)

# we simplify the results of the processing function here. This way, we can do
# more complex behavior, like weighting different metrics against one another,
# maybe?
def fitness(wiresInput):
    wires, wireLength, mean_gain, max_gain, min_gain = processAntenna(wiresInput)
    return -mean_gain

def lengthOfSegments(wires):
    segment = 1
    previous = (0.0, 0.0, 0.0)
    for x2,y2,z2 in wires:
        x1,y1,z1 = previous
        length = sqrt(((x1 - x2)**2) + ((y1 - y2)**2) + ((z1 - z2)**2))
        previous = (x2, y2, z2)
        print(f"segment {segment}: {length:.5} meters, or {(length * 39.37):.5} inches")
        segment += 1

if __name__=='__main__':
    
    # until I come up with a better way of doing this, I'll record my finished
    # antennas here:
    uhf_high_gain = [
        -0.05349006, -0.02630232, 0.09886351,
        -0.09748259, 0.09630158, 0.00102119,
        0.09976958, -0.09852782, 0.032572
    ]

    noaaSatelliteAntenna = [
        0.06007878, 0.05595085, 0.0722251,
        -0.08225932, -0.05269982, 0.01606696,
        0.08835985, 0.0832063, 0.01526375
    ]

    goesSatelliteAntenna = [
        -0.08995548, -0.16057963, 0.44024533,
        -0.48341465, -0.30803703,  0.31034775,
        0.44899531, -0.08152924, 0.08007004
    ]
    # I've now confirmed--xnec says that this has two radiation spikes at
    # around 45 degrees up, and another one at 45 degrees down on the other
    # side. It's actually pretty cool.

    testingAntenna = goesSatelliteAntenna

    wires, wireLength, mean_gain, max_gain, min_gain = processAntenna(testingAntenna)
    print(f"mean:{mean_gain:.5}\nmax:{max_gain:.5}\nmin:{min_gain:.5}\ntotal wire length:{wireLength:.5} meters, or {(wireLength * 39.37):.5} inches\n")
    lengthOfSegments(wires)
    print("overall fitness:", round(fitness(testingAntenna), 3))
