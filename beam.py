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
import parameter as loadparameterfile

#create global variables of parameters to be read in

BEAM_CURRENT_DENSITY = None
FWHM = None
SCAN_WIDTH = None
BEAM_CURRENT = None
BEAM_CENTER = None
ERF_BEAM_WIDTH = None
BEAM_TYPE = None


def init():
    loadparameterfile.init()
    parameterdict = loadparameterfile.toDict()
    
    #modify namespace to use global variables
    global BEAM_CURRENT_DENSITY
    global FWHM
    global SCAN_WIDTH
    global BEAM_CURRENT
    global BEAM_CENTER
    global ERF_BEAM_WIDTH
    global BEAM_TYPE
    
    BEAM_CURRENT_DENSITY = float(parameterdict['BEAM_CURRENT_DENSITY'])
    FWHM = float(parameterdict['FWHM'])
    SCAN_WIDTH = float(parameterdict['SCAN_WIDTH'])
    BEAM_CURRENT = float(parameterdict['BEAM_CURRENT'])
    BEAM_CENTER = float(parameterdict['BEAM_CENTER'])
    ERF_BEAM_WIDTH = float(parameterdict['ERF_BEAM_WIDTH'])
    BEAM_TYPE = str(parameterdict['BEAM_TYPE'])

def sigma_by_fwhm():
    return FWHM/(math.sqrt(8 * math.log(2)))
    
def get_beam(x):
    if BEAM_TYPE == 'constant':
        return homogenous_beam()
    elif BEAM_TYPE == 'gaussian':
        return gaussian_beam(x)
    elif BEAM_TYPE == 'error function':
        return erf_beam(x)
    
def gaussian_beam(x):
    return ((BEAM_CURRENT/constants.e)/(math.sqrt(2*constants.pi) * sigma_by_fwhm() * SCAN_WIDTH)) * math.exp(-((x - BEAM_CENTER)**2)/(2*(sigma_by_fwhm()**2))) 

def erf_beam(x):
    x1 = BEAM_CENTER - ERF_BEAM_WIDTH/2
    x2 = BEAM_CENTER + ERF_BEAM_WIDTH/2
    return ((BEAM_CURRENT/constants.e)/(2*SCAN_WIDTH*ERF_BEAM_WIDTH)) *(math.erf(-(x-x2)/(math.sqrt(2) * sigma_by_fwhm())) - math.erf(-(x-x1)/(math.sqrt(2) * sigma_by_fwhm())))

def homogenous_beam():
    return BEAM_CURRENT_DENSITY/constants.e
