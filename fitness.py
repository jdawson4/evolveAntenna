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
    # (higher gain required for higher frequencies because of atmospheric attenuation!)

    # sorta want these as parameters but whatever
    frequency=54
    #polarizationType=''
    polarizationType='LIN'

    # we have to do some weird preprocessing because the library we're
    # using is based on compiled c/fortran code so it's finicky.
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
        
        # here we define the frequencies we're looking for. The parameters here
        # define a frequency, and then x other frequencies y steps above that
        # base frequency. Important! This defines how broad of a band our
        # antenna works for!
        #handle_nec(necpp.nec_fr_card(context, 0, 5, 137, 0.25)) # checks the 137MHz, as well as 4 frequencies 0.25 mhz higher, to cover the entire LEO weather satellite band.
        handle_nec(necpp.nec_fr_card(context, 0, 100, 54, 6)) # checks 100 frequencies above the 54MHz, each 6 MHz apart

        
        # Polarization determines A LOT about antenna architecture. We have
        # options for prcessing left-handed, right-handed, and linear
        # polarization.
        # Left- and right-handed are used by satellites, whereas most
        # terrestrial applications are linearly polarized. Natural radio
        # sources tend to be unpolarized, but there are exceptions!
        if polarizationType=='RHP':
            polarization=2
        elif polarizationType=='LHP':
            polarization=3
        elif polarizationType=='':
            polarization=1
        elif polarizationType=='LIN':
            polarization=1
        else:
            polarization=1
        # here's where polarization gets applied
        handle_nec(necpp.nec_ex_card(context, polarization, 36, 36, 0, 0, 0, 0, 10, 10, 0))


        # this is... quite important. It describes the radiation patterns, particularly where they're coming from.
        #handle_nec(necpp.nec_rp_card(context, 0, 10, 10, 0,5,0,0, 0, 0, 18, 36, 0, 0)) # all angles above the ground? (satellites)
        handle_nec(necpp.nec_rp_card(context, 0, 10, 10, 0,5,0,0, 60, 0, 6, 36, 0, 0)) # only 30 degrees above ground? (terrestrial signals)
        
        
        # here's the important part:
        mean_gain = necpp.nec_gain_mean(context, 1)
        max_gain = necpp.nec_gain_max(context, 1)
        min_gain = necpp.nec_gain_min(context, 1)
        # MEAN gain in order to make an omnidirectional... but there again it might just maximize a node still?
        # MAX gain to make a directional antenna,
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

if __name__=='__main__':
    
    # until I come up with a better way of doing this, I'll record my finished
    # antennas here:
    #
    # these commented-out antennas are basically useless; they are evolved to
    # receive terrestrial tv signals from 60 degrees above the horizon. You may
    # notice that no tv signals come from that region of the sky!
    '''
    # 5 wires, evolved for min gain, for tv frequencies:
    tvAntenna5Wires_minGain = [-0.2170649,0.08211413,0.11587374,0.11032273,-0.00727395,0.39316114,0.38241553,-0.13979879,0.32285156,0.37539444,0.1980235,0.18295936,0.25851554,0.10262777,0.31215069]
    
    # 3 wires, evolved for min gain, for tv frequencies:
    tvAntenna3Wires_minGain = [-0.36813742,0.04660534,0.20281676,0.36912827,-0.05468209,0.38111223,0.29000245,-0.32773359,0.16520391]
    
    # 3 wires, evolved for mean gain, for tv frequencies:
    tvAntenna3Wires_meanGain = [-0.35906988,-0.15302196,0.16442577,0.35571068,0.0245733,0.29642038,0.33722326,0.34880001,0.10220936]
    
    # 3 wires evolved for mean for TV frequencies, but the y axis has been
    # restricted to 0. This antenna is 2D!
    tvAntenna3Wires_meanGain_xzPlain = [0.38845274,0,0.21796932,-0.39259615,0,0.39595648,-0.39406343,0,0.10534551]
    '''
    # these antennas have been evolved to receive tv signals transmitted from 0
    # to 30 degrees above the horizon:
    tvAntenna3Wires_meanGain_xzPlain = [-0.02611375,0,0.04229337,-0.02961295,0,0.05809941,-0.09029584,0,0.05111244]


    wires, wireLength, mean_gain, max_gain, min_gain = processAntenna(tvAntenna3Wires_meanGain_xzPlain)
    print(f"mean:{mean_gain}\nmax:{max_gain}\nmin:{min_gain}\ntotal wire length:{wireLength} meters")
