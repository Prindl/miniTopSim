#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  delooping.py
#  
#  PUSZTAI Daniel
#

import numpy as np
import sys
import parameter as par

def get_intersection(xPoints, yPoints):
    """
    Get the intersecting point of two segments.
    
    xPoints holds a list of four points (Point 1 and 2 of Segment 1,
    Point 3 and 4 of Segment 2).
    
    yPoints holds the corresponding y values for the xPoints.
    
    Returns the point as a pair of values: (x, y)
    If there is no intersection, returns None.
    """
    
    # Get the two coefficient matrices for the linear equation (A*t=b)
    A = np.array([[xPoints[1] - xPoints[0], xPoints[2] - xPoints[3]], \
    [yPoints[1] - yPoints[0], yPoints[2] - yPoints[3]]])
    
    b = np.array([xPoints[2] - xPoints[0], yPoints[2] - yPoints[0]])
    
    # Calculate the solution (t) of the linear equations
    if np.linalg.det(A) != 0:
        t = np.linalg.solve(A, b)
        
        # Check if there is an intersection
        if t[0] >= 0 and t[0] < 1 and t[1] >= 0 and t[1] < 1:
            # Calculate the position (x, y) of the intersection
            result = (xPoints[0] + (xPoints[1] - xPoints[0]) * t[0], \
            yPoints[0] + (yPoints[1] - yPoints[0]) * t[0])
        else:
            result = None
    else:
        # No solution (A=singular matrix)
        result = None
    
    return result

def deloop(xPoints, yPoints):
    """
    Loop through the given points (x and y) and check for intersections.
    Remove all loops and return the new pair of x and y points.
    """
    
    # Check if input variables have right size
    if len(xPoints) != len(yPoints):
        raise ValueError("Number of x-Points does not match number of y-points!")
    
    loops=[]        # Start and end point of loops (start, end)
    loopPoints=[]   # Intersection points of loops (x, y)
    
    if par.NUMPY:        
        # Solve the problem with NumPy whole-array operations (faster)
        dim=len(xPoints)
        
        # Arrays for the linear equation coefficient matrix (A) and vector (b)
        A = np.empty((dim-1, dim-1, 2, 2))
        b = np.empty((dim-1, dim-1, 2))
        
        # Mask to eliminate same and nearby segments and singular matrices (A)
        calcMask = np.full((dim-1, dim-1), False, dtype = bool)
        
        # Array for the solution of the linear equations (intersection parameter)
        t = np.full((dim-1, dim-1, 2), -1.0)
        
        # Array for finding the x- and y-points to a segment
        indexArray = np.empty((dim-1, dim-1, 2), dtype = int)
        
        # Fill arrays with the starting values
        for i in range(dim-1):
            for j in range(i+2, dim-1):
                b[i][j] = np.array((xPoints[j] - xPoints[i], yPoints[j] - yPoints[i]))
                A[i][j] = np.array(((xPoints[i+1] - xPoints[i], xPoints[j] - xPoints[j+1]), \
                (yPoints[i+1] - yPoints[i], yPoints[j] - yPoints[j+1])))
                
                calcMask[i][j] = True
                
                indexArray[i][j] = np.array((i, j))
        
        # Mask all singular matrices
        calcMask = calcMask & (np.linalg.det(A) != 0)
        
        # Calculate solutions
        t[calcMask] = np.linalg.solve(A[calcMask], b[calcMask])
        
        # Get all intersections (solution of equation 0 <= t <= 1)
        intersectionMask = (t >= 0) & (t < 1)
        intersectionMask = (intersectionMask.T[0] & intersectionMask.T[1]).T
        
        # Return resulting intersection points (indices and coordinates)
        for loop, solution in zip(list(indexArray[intersectionMask]), list(t[intersectionMask])):
            loops.append((loop[0] + 1, loop[1]))
            loopPoints.append((xPoints[loop[0]] + (xPoints[loop[0] + 1] - xPoints[loop[0]]) * solution[0], \
            yPoints[loop[0]] + (yPoints[loop[0] + 1] - yPoints[loop[0]]) * solution[0]))
        
    else:
        # Iterate through all possible Segment combinations
        for i in range(len(xPoints)-1):
            for j in range(i+2, len(yPoints)-1):
                point = get_intersection(xPoints[i:i+2] + xPoints[j:j+2], \
                yPoints[i:i+2] + yPoints[j:j+2])
                
                if point != None:
                    loops.append((i+1, j))
                    loopPoints.append(point) 
    
    # Create a mask for the points to delete the loops
    loopMask = [True for i in range(len(xPoints))]
    
    for loop, point in zip(loops, loopPoints):
        loopMask[loop[0]+1:loop[1]+1] = [False for i in range(loop[1] - loop[0])]
        
        # Replace coordinates of 1st loop point with intersection point
        xPoints[loop[0]] = point[0]
        yPoints[loop[0]] = point[1]
    
    # Create a new list and store the new points (without loops)
    xResult=[]
    yResult=[]
    
    for x, y, mask in zip(xPoints, yPoints, loopMask):
        if mask:
            xResult.append(x)
            yResult.append(y)
    
    return xResult, yResult
