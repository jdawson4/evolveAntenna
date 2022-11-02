# Author: Jacob Dawson
#
# The idea of this file is to define a function which determines the "fitness"
# of a given antenna given a set of parameters (frequency, gain, whatever).
# We're going to be using the necpp library for this. This function will be
# what we optimize upon! Not sure how machine-learning our optimiziation will
# get, but we can consider this the "loss" we are minimizing.

import necpp

# below is some example code from necpp itself.
# Maybe it'll show me enough to proceed?
def handle_nec(result):
    if (result != 0):
        print(necpp.nec_error_message())
 
def frequency_response():
    # Scan through frequencies from 1 to 30 MHz
    for f in range(1,30):
        nec = necpp.nec_create()
        handle_nec(necpp.nec_wire(nec, 1, 17, 0, 0, 2, 0, 0, 11, 0.1, 1, 1))
        handle_nec(necpp.nec_geometry_complete(nec, 1))
        handle_nec(necpp.nec_gn_card(nec, 1, 0, 0, 0, 0, 0, 0, 0))
        handle_nec(necpp.nec_fr_card(nec, 0, 1, f, 0))
        handle_nec(necpp.nec_ex_card(nec, 0, 0, 5, 0, 1.0, 0, 0, 0, 0, 0))
        handle_nec(necpp.nec_rp_card(nec, 0, 90, 1, 0,5,0,0, 0, 90, 1, 0, 0, 0))
        result_index = 0
        z = complex(necpp.nec_impedance_real(nec,result_index), necpp.nec_impedance_imag(nec,result_index))
        print("f=%0.2fMHz \t(%6.1f,%+6.1fI) Ohms" % (f, z.real, z.imag))
        necpp.nec_delete(nec)

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
    epsilon = 0.00001 # this parameter makes sure that we're not inserting wires that are too similar!

    # we have to do some weird preprocessing because the library we're
    # using is based on compiled c/fortran code so it's finicky.
    if len(wiresInput)<3:
        #print(999)
        return 999
    elif isinstance(wiresInput[0], tuple):
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
        i=1
        for x2, y2, z2 in wires:
            if z2 < 0:
                #print(999)
                return 999 # can't go below ground!
            x1, y1, z1 = previousEnd
            handle_nec(necpp.nec_wire(context, i, 15, x1, y1, z1, x2, y2, z2, 0.001, 1, 1))
            previousEnd = (x2, y2, z2)
            i+=1
        handle_nec(necpp.nec_geometry_complete(context, 1)) # says that we've now set the antenna geometry
        handle_nec(necpp.nec_gn_card(context, 1, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)) # defines ground plane as an infinite surface. Much simpler that way.
        
        # here we define the frequencies we're looking for. The parameters here
        # define a frequency, and then x other frequencies y steps above that
        # base frequency. Important! This defines how broad of a band our\
        # antenna works for!
        #handle_nec(necpp.nec_fr_card(context, 0, 5, frequency, 0.25)) # checks the base frequency, as well as 4 frequencies 0.25 mhz higher
        handle_nec(necpp.nec_fr_card(context, 0, 100, frequency, 6)) # checks 100 frequencies above the given freq, each 6 MHz apart. For tv, input 54 as base frequency.

        
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


        handle_nec(necpp.nec_ex_card(context, polarization, 36, 36, 0, 0, 0, 0, 10, 10, 0)) # here's where polarization gets applied
        handle_nec(necpp.nec_rp_card(context, 0, 90, 1, 0,5,0,0, 0, 90, 1, 0, 0, 0)) # this is... quite important. It describes the radiation patterns--gain and so on. I can't quite work it out, but this is crucial.
        
        
        # here's the important part:
        gain = necpp.nec_gain_mean(context, 1)
        #gain = necpp.nec_gain_max(context, 1)
        #gain = necpp.nec_gain_min(context, 1)
        # MEAN gain in order to make... something
        # MAX gain to make a directional antenna,
        # MIN gain to make an omnidirectional? Not too sure!

        necpp.nec_delete(context) # delete now that we have our calculations
    except:
        #print(999)
        return 999.0
        # if the processing gets fucked up, we just want to make the alg know
        # that that antenna is invalid.
    
    #print(gain)

    return -gain
    # I am slightly lying--we return gain... negated, so that our model
    # can *minimize* the negative gain (that is, maximize the gain.)
    # This weird inversion is happening because most optimization algorithms
    # are actually seeking to minimize mathematical functions.

if __name__=='__main__':
    #gain = fitness(frequency=137, polarizationType='RHP', wires=[(0.5,0.5,0.5),(1,1,1)])
    gain = fitness(wiresInput=[0.0,0.3,1.3])
    print(gain)
