# -*- coding: utf-8 -*-
"""
This module implements three variants of ion beams.
Beam type depends on parameter read from config file:
[BEAM] BEAM_TYPE

constant: homogen beam
gaussian: beam is presented by gaussian distrubution
error_function: approximation of gaussian beam by two error functions

module beam.py implements these methods:

    get_beam(template)
        calculates the beam at all x positions
"""

'''
	import needed modules
	scipy.constants provides constants: c0, e, µ0,...
	math implements basic math functions: exp(), sqrt(), ln(), erf(),...
	scipy.special.erf method provides a method for calculating erf with numpy arrays
'''
import math
import parameter as par
import numpy as np
from scipy.special import erf
from scipy.constants import pi, e

    
'''
	depending on the parameter BEAM_TYPE a beam function is selected
'''
def get_beam(xvals):
    sigma = par.FWHM/(math.sqrt(8 * math.log(2))) #standard deviation
    x1 = np.full_like(xvals, par.BEAM_CENTER - par.ERF_BEAM_WIDTH/2)
    x2 = np.full_like(xvals, par.BEAM_CENTER + par.ERF_BEAM_WIDTH/2)    
    try:
        if par.BEAM_TYPE == 'constant':
            return par.BEAM_CURRENT_DENSITY/e
            
        elif par.BEAM_TYPE == 'gaussian':
            return (par.BEAM_CURRENT/e)/(math.sqrt(2*pi) * sigma * par.SCAN_WIDTH) * np.exp(-((xvals - np.full_like(xvals, par.BEAM_CENTER))**2)/(2*(sigma**2)))
        
        elif par.BEAM_TYPE == 'error function':
            return ((par.BEAM_CURRENT/e)/(2*par.SCAN_WIDTH*par.ERF_BEAM_WIDTH)) * (erf(-(xvals-x2)/(math.sqrt(2) * sigma)) - erf(-(xvals-x1)/(math.sqrt(2) * sigma)))
        
        else:
            print('error: beam type could not be identified')
            exit(-1)
    except ZeroDivisionError as ZDE:
        print(ZDE.args)
    
