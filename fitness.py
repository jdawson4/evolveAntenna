# Author: Jacob Dawson
#
# The idea of this file is to define a function which determines the "fitness"
# of a given antenna given a set of parameters (frequency, gain, whatever).
# We're going to be using the necpp library for this. This function will be
# what we optimize upon! Not sure how machine-learning our optimiziation will
# get, but we can consider this the "loss" we are minimizing.

import necpp
from shapely.geometry import LineString

def handle_nec(result):
    if (result != 0):
        print(necpp.nec_error_message())

# some dirty code for computing if two wires intersect:
def linesIntersect(a,b):
    x = LineString(a)
    y = LineString(b)
    return x.crosses(y)

def fitness(wiresInput=[(1, 1, 1), (2, 2, 2)]):
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
    '''allCoords = []
    for coords in wires:
        for coord in coords:
            if coord == 0.0:
                #print('ignoring')
                continue
            else:
                for c in allCoords:
                    if abs(c - coord) < epsilon:
                        print(999)
                        #print('here!')
                        return 999
            allCoords.append(coord)'''
    #print(wires)

    try:
        context = necpp.nec_create()
        previousEnd = (0, 0, 0)
        lines = []
        i=1
        for x2, y2, z2 in wires:
            if z2 <= 0.0:
                #print(999)
                return 999 # can't go below ground!
            x1, y1, z1 = previousEnd
            newestLine = ((x1,y1,z1), (x2,y2,z2))
            for line in lines:
                if linesIntersect(newestLine, line):
                    #print(newestLine, line)
                    return 999 # wires can't intersect! Short circuiting is bad!
            lines.append(newestLine)
            handle_nec(necpp.nec_wire(context, i, 15, x1, y1, z1, x2, y2, z2, 0.001, 1, 1))
            previousEnd = (x2, y2, z2)
            i+=1
        handle_nec(necpp.nec_geometry_complete(context, 1)) # says that we've now set the antenna geometry
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
        handle_nec(necpp.nec_rp_card(context, 0, 10, 10, 0,5,0,0, 0, 0, 18, 36, 0, 0)) # I believe that this specifies that it's coming from all angles above the ground?
        
        
        # here's the important part:
        gain = necpp.nec_gain_mean(context, 1)
        #gain = necpp.nec_gain_max(context, 1)
        #gain = necpp.nec_gain_min(context, 1)
        # MEAN gain in order to make... something
        # MAX gain to make a directional antenna,
        # MIN gain to make an omnidirectional? Not too sure!

        necpp.nec_delete(context) # delete now that we have our calculations
    except Exception as e:
        #print(999)
        print(e)
        return 999.0
        # if the processing gets fucked up, we just want to make the alg know
        # that that antenna is invalid.
    
    return -gain
    # we return gain negated, so that our model can *minimize* the negative
    # gain (that is, maximize the gain.)

if __name__=='__main__':
    gain = fitness(wiresInput=[0.0,0.3,1.3])
    print(gain)
