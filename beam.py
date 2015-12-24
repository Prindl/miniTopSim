# -*- coding: utf-8 -*-
"""
This module implements three variants of ion beams.
Beam type depends on parameter read from config file:
[BEAM] BEAM_TYPE
constant: homogen beam
parameter:
    -[BEAM] BEAM_CURRENT_DENSITY
gaussian: beam is presented by gaussian distrubution
parameter:
    -[BEAM] BEAM_CURRENT
    -[BEAM] SCAN_WIDTH
    -[BEAM] BEAM_CENTER
    -[BEAM] FWHM
error_function: approximation of gaussian beam by two error functions
parameter:
    -[BEAM] BEAM_CURRENT
    -[BEAM] SCAN_WIDTH
    -[BEAM] BEAM_CENTER
    -[BEAM] FWHM
    -[BEAM] ERF_BEAM_WIDTH
    
module beam.py implements these methods:
    init()
        initializes the parameter.py module and loads parameters
    get_beam(x)
        calculates the beam at x according to set parameters
    
"""

#import needed modules
#scipy.constants provides constants: c0, e, µ0,...
#math implements basic math functions: exp(), sqrt(), ln(), erf(),...
import scipy.constants as constants
import math
import parameter as par


def sigma_by_fwhm():
    return par.FWHM/(math.sqrt(8 * math.log(2)))
    
def get_beam(x):
    if par.BEAM_TYPE == 'constant':
        return homogenous_beam()
    elif par.BEAM_TYPE == 'gaussian':
        return gaussian_beam(x)
    elif par.BEAM_TYPE == 'error function':
        return erf_beam(x)
    
def gaussian_beam(xvals):
    beam= []
    for x in xvals:
        beam.append( ((par.BEAM_CURRENT/constants.e)/(math.sqrt(2*constants.pi) * sigma_by_fwhm() * par.SCAN_WIDTH)) * math.exp(-((x - par.BEAM_CENTER)**2)/(2*(sigma_by_fwhm()**2))) )
    return beam    
    
def erf_beam(xvals):
    beam= []
    x1 = par.BEAM_CENTER - par.ERF_BEAM_WIDTH/2
    x2 = par.BEAM_CENTER + par.ERF_BEAM_WIDTH/2
    for x in xvals:
        beam.append(((par.BEAM_CURRENT/constants.e)/(2*par.SCAN_WIDTH*par.ERF_BEAM_WIDTH)) *(math.erf(-(x-x2)/(math.sqrt(2) * sigma_by_fwhm())) - math.erf(-(x-x1)/(math.sqrt(2) * sigma_by_fwhm()))) )
    return beam
    
def homogenous_beam():
    return par.BEAM_CURRENT_DENSITY/constants.e
