# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 00:53:23 2015

@author: Maximilian Prindl
"""

import math

def cosine(x):
    return math.cos(x)
def doubleCosine(x):
    return math.cos(x*2+math.pi)
    # We define step function as ternary function like:
    # f(x) = (x >= 0) ? 1 : 0
    # For making compliant with previous calculations,
    # we modify the step function to generate [-1, +1] for [-PI, +PI] inputs
def step(x):
    #return 2*(1 if x >= 0 else 0)-1
    if x >= 0:
        return 1
    return -1
    
    # We define V-shape as triangle function which is defined as follow:
    # f(x) = |x|
    # For making compliant with previous calculations,
    # we modify the V-shape function to generate [-1, +1] for [-PI, +PI] inputs
def vShape(x):
    return -2*abs(x / math.pi)+1
def default(x):
    return x
