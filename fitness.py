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

def fitness(frequency=137, polarizationType='', wires=[(1, 1, 1), (2, 2, 2)]):
    context = necpp.nec_create()
    previousEnd = (0, 0, 0)
    i=1
    for x2, y2, z2 in wires:
        x1, y1, z1 = previousEnd
        handle_nec(necpp.nec_wire(context, i, 15, x1, y1, z1, x2, y2, z2, 0.005, 1, 1))
        previousEnd = (x2, y2, z2)
        i+=1
    handle_nec(necpp.nec_geometry_complete(context, 1)) # says that we've now set the antenna geometry
    handle_nec(necpp.nec_gn_card(context, 1, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)) # quadruped ground plane where each wire is 5 mm in radius and .5 meters long
    handle_nec(necpp.nec_fr_card(context, 0, 5, frequency, 0.25)) # checks the base frequency, as well as 4 frequencies 0.25 mhz higher
    if polarizationType=='RHP':
        polarization=2
    else:
        polarization=0
    handle_nec(necpp.nec_ex_card(context, polarization, 1, 1, 0, 1.0, 0, 0, 0, 0, 0)) # I have no idea what this does. Something to do with excitation? Polarization?
    handle_nec(necpp.nec_rp_card(context, 0, 90, 1, 0,5,0,0, 0, 90, 1, 0, 0, 0)) # this is... quite important. It describes the radiation patterns--gain and so on. I can't quite work it out, but this is crucial.
    
    # from the example, so maybe ignore:
    #z = complex(necpp.nec_impedance_real(context,result_index), necpp.nec_impedance_imag(context,result_index))
    #print("f=%0.2fMHz \t(%6.1f,%+6.1fI) Ohms" % (frequency, z.real, z.imag))
    
    # here's the important part:
    gain = necpp.nec_gain_mean(context, 0)

    necpp.nec_delete(context) # delete now that we have our calculations

    return gain

if __name__=='__main__':
    gain = fitness()

    print(gain)
