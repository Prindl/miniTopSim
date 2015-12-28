# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 00:46:34 2015

@author: Maximilian Prindl
         Peter Resutik, 1126613
         Roman Gehrer
"""
import csv
import numpy as np
import parameter as par
import functions
from delooping import deloop
from math import pi
from adaptive_grid import adapt, anglebisect
from sputter import sputterVelocity



class surface:
    """
    Properties: xvals, yvals, xs, ys
    The xvalues and yvales of a surface and the corresponding anglebisectors.
    
    """
    
    def __init__(self):
        interval_start = par.XMIN
        interval_end = par.XMAX
        period = interval_start - interval_end
        assert period != 0, 'Error period is 0.'
        interval_step = par.DELTA_X
        amplitudePP = par.FUN_PEAK_TO_PEAK
        self.surfaceType = par.INITIAL_SURFACE_TYPE
        self.surfaceFile = par.INITIAL_SURFACE_FILE
        #arange() creates a half-open interval, which excludes the endpoint
        self.xvals = np.arange(interval_start, interval_end + interval_step, interval_step)
        self.yvals = np.zeros_like(self.xvals)
        
        func = functions.default
        if par.INITIAL_SURFACE_TYPE == 'Cosine':
            func = functions.cosine
        elif par.INITIAL_SURFACE_TYPE == 'DoubleCosine':
            func = functions.doubleCosine
        elif par.INITIAL_SURFACE_TYPE == 'Step':
            func = functions.step
        elif par.INITIAL_SURFACE_TYPE == 'V-Shape':
            func = functions.vShape        
        
        for i, x in enumerate(self.xvals):
            self.yvals[i] = amplitudePP * (1 + func(x * 2*pi / period) )
        #Berechne Winkelsymmetralen
        self.xs, self.ys = anglebisect(self.xvals, self.yvals)
        #Falls Adaptives Grid gewünscht, passe Werte an
        if par.ADAPTIVE_GRID:
            adapt(self)
    
    @property
    def xvals(self):
        return self._xvals
        
    @xvals.setter
    def xvals(self, x):
        self._xvals = x
        
    @property
    def yvals(self):
        return self._yvals
        
    @yvals.setter
    def yvals(self, y):
        self._yvals = y
        
    @property
    def xs(self):
        return self._xs
    
    @xs.setter
    def xs(self, xsym):
        self._xs = xsym
    
    @property
    def ys(self):
        return self._ys
    
    @ys.setter
    def ys(self, ysym):
        self._ys = ysym
        
    
    def __repr__(self):
        #string = 'surfaceConfig: {0}\nsurfaceFile: {1}\ninterval [{2}...{3}]\n'.format(self.surfaceType, self.surfaceFile, self.xvals[0], self.xvals[-1])
        string = "Len(xvals): {0}, Len(yvals): {1}, Len(xs): {2}, Len(ys): {3}".format( len(self.xvals), len(self.yvals), len(self.xs), len(self.ys))      
        return string
        
    def get_surfaceFile(self):
        return self.surfaceFile
        
    def write(self, file, time):
        '''
        This function writes the points of a surface at a given time in a .srf file.
        Format:
        surface: time, number of points, x-positions y-positions
        x[0] y[0]
        x[1] y[1]
        ...
        x[npoints-1] y[npoints-1]
        
        >>>surface1.write(file, time)
        '''
        file.writelines('surface: {0}, {1}, x-points y-points \n'.format(time, len(self.xvals)))
        writer = csv.writer(file, lineterminator='\n', delimiter=' ')
        
        for x, y in zip(self.xvals, self.yvals):
            writer.writerow([x, y])
                
        
    def movePointsByDirection(self, ds):
        '''
        Moves all points of a surface by ds in the direction of [xs, ys].
        
        xs: the x coordinate of the direction
        ys: the y coortinate of the direction
        ds: the length of the movement
        
        >>>surface1.movePointsByDirection(ds)
        
        '''
        self.xvals = self.xvals + self.xs * ds
        self.yvals = self.yvals + self.ys * ds
                
    def process(self, timestep=1):
        '''    
        Processes the surface depending whether par.ETCHING is set or not.
        
        When the initialTime is specified 
    
        par.ETCHING = True -> etching
        par.ETCHING = False-> Sputtern

        When a file is specified, the process is written to a file after each step.
        >>>surface.process(time, step)
        '''
                
        if par.ETCHING:
            vn = par.ETCH_RATE
        else:
            vn = sputterVelocity(self)
            assert len(vn) > 0, 'Error: vn could not be calculated!'
                    
        self.movePointsByDirection(vn*timestep)
                
        if not par.NUMPY:
            #Umwandlung da delopping ein Liste für korrekte Funktion braucht, wenn par.NUMPY=False
            self.xvals, self.yvals = np.array(deloop(list(self.xvals), list(self.yvals)))
        else:
            self.xvals, self.yvals = deloop(self.xvals, self.yvals)
            
        #Berechne neue Winkelsymmetralen für die neuen x & y werte
        self.xs, self.ys = anglebisect(self.xvals, self.yvals)

        #Falls die Funktion Adaptive Gitter erwünscht ist, passe Knoten (und Winkelsymmetralen) an
        if par.ADAPTIVE_GRID:
            adapt(self)
