# -*- coding: utf-8 -*-
"""
Created on Thu Dec 24 11:58:30 2015

@author: max
"""
import parameter as par
import numpy as np
from beam import get_beam

def sputterYield(cos_theta):
    '''
    Calculates the SputterYield for a given angle with the parameters specified in the config file.
    
    >>>surface.sputterYield(cos_theta)
    Note that the cos_theta is the inner product of the unit vectors of the given angle and not the angle itself.
    '''
    Y0 = par.SPUTTER_YIELD_0
    f = par.SPUTTER_YIELD_F
    b = par.SPUTTER_YIELD_B
    return Y0*cos_theta**-f*np.exp(b*(1-1/cos_theta))
    
def sputterVelocity(surface):
    '''
    Berechnet die Normalengeschwindigkeit beim Sputtern.
    Parameter:
    xs, ys Normalenrichtung der Oberfläche
        
    Fbeam Strahlstromdicht [Atome/(cm^2*s)] aus ConfigFile
    N Atomdichte des Materials [Atome/cm^3] aus Configfile
        
    Ausgabe:
    vn Normalengeschwindigkeit [nm/s]
    '''
    Fbeam = get_beam(surface.xvals)
    N = par.DENSITY
    Xspu = 0; Yspu = -1 #Sputterrichtung: feste Werte aus Angabe
    cos_theta = Xspu * surface.xs + Yspu * surface.ys
    Fsput = Fbeam * sputterYield(cos_theta) * cos_theta
    vn = Fsput / N * 1e7 #1e7 Umrechnung cm -> nm
    return vn
