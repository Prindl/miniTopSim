# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 23:11:43 2015
Test for the Surface class.
@author: Maximilian Prindl
"""

import os

import parameter as par
import matplotlib.pyplot as plt
from numpy import arange
from surface import surface as Surface
import beam

def test_surface():    
    dir_path = os.path.dirname(os.path.abspath(__file__))
    par.init()
    par.read(os.path.join(dir_path, 'test_surface.cfg'))

    surface = Surface()
    print('PRESS ANY KEY TO EXIT THE PLOT')
    for t in arange(1, par.TOTAL_TIME + par.TIME_STEP, par.TIME_STEP):
        surface.process(par.TIME_STEP)
        plt.title('Test Surface{0}'.format(t))
        plt.plot(surface.xvals, surface.yvals, '.r-')
        plt.xlabel('x')
        plt.ylabel('y')
        plt.connect('key_press_event', event)
        plt.show()

def event(event):
    if event:
        if event.key is not None:
            plt.close()
    

if __name__ == '__main__':
    test_surface()
