# Author: Jacob Dawson
# The idea of this file is to define a function which determines the "fitness"
# of a given antenna given a set of parameters (frequency, gain, whatever).
# We're going to be using the necpp library for this. This function will be
# what we optimize upon! Not sure how machine-learning our optimiziation will
# get, but we can consider this the "loss" we are minimizing.

import necpp

def fitness():
    return 0.0


# below is some example code from necpp itself.
# Maybe it'll show me enough to proceed?
def handle_nec(result):
    if (result != 0):
        print nec_error_message()
 
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
        print "f=%0.2fMHz \t(%6.1f,%+6.1fI) Ohms" % (f, z.real, z.imag)
        necpp.nec_delete(nec)
