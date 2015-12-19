# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 00:46:34 2015

@author: Maximilian Prindl
"""

import sys
import os
import re
import csv
import matplotlib.pyplot as plt

class plot:
    
    def __init__(self, filename):
        '''
        returns plot object. Each plot object has one surface.srf.
        
        filename is the file name e.g. trench.srf
        
        usage:
        >>>plot(surface.srf)
        '''
        self.filename = filename
        self.xvals = list()
        self.yvals = list()
        self.filepath = self.get_filepath(filename)
        self.surfaceNumber = self.count_surfaces()
        
        for number in range(1, self.surfaceNumber + 1):
            xtmp, ytmp = self.get_surfacedata(number)
            self.xvals.append(xtmp)
            self.yvals.append(ytmp)
        
        self.plot_index = 0
        self.aspect = 0
        self.clear_figure = 1
        self.axis = False
        self.saveAxis = [-60, 60 -120, 20]
        
    def __repr__(self):
        string = 'Surfacefile: {0}\nNumber of surfaces: {1}\n'.format(self.filename, self.surfaceNumber)
        return string

    def plot(self, multiview = False):
        '''
        Plotten der Oberflaeche:
    
        plot(multiview=False)
    
            multiview: True: Two plotfields side by side; False: One single plotfield
    
        - Space-bar: show next surface.
        - '[1-9]': show every 2nd surface
        - '0': show last surface
        - 'r': show first surface
        - 'a': switch plot aspect 1:1 <==> auto
        - 'c': switch between two modi, single plot, multiple plot for surfaces
        - 'f': save plot as (png-)file with the name of the xxx.srf file
        - 'b': switch between fixed axis and auto axis of new surface
        - 'q': Quit.
        '''
        help(plot.plot)
        if not multiview:
            self.multi = False
            self.ax1 = plt.subplot(1, 1, 1)
        else:
            self.multi = True
            self.ax1 = plt.subplot(1, 2, 1)
            self.ax2 = plt.subplot(1, 2, 2)
        self.event_handler(None)
        plt.connect('key_press_event', self.event_handler)
        plt.show()
    
    def get_filepath(self, datafile_arg):
        '''
        Returns absolute path of the surface.
        '''
    	# get the absolute path of data-file
        dir_path = os.path.dirname(os.path.abspath(__file__))
    	# extend the path with the file, operating system independently 
        filepath = os.path.join(dir_path, datafile_arg)
        return filepath
    
    
    def count_surfaces(self):
        '''
        Counts surfaces in a file(.srf).
        '''
    	# gets the number of surfaces that are available
        hit_count = 0
        with open(self.filepath, "r") as file:
            for line in file:
                if re.match("surface(.*)", line):
                    hit_count += 1
        return hit_count
    
    def get_surfacedata(self, surface_number):
        '''
        Loads surface points from a file(.srf).
        '''
    # parse data from xxx.srf file
        linenumber = 0
        x = list()
        y = list()
        with open(self.filepath, "r") as file:
            reader = csv.reader(file, delimiter=' ')
            for line in file:
    		# search for "surface" to extract data
                if re.match("surface(.*)", line): 
                    linenumber += 1
    
                if surface_number == linenumber:
                    for row in reader:
                        if not re.match("surface(.*)",row[0]):
                            x.append(float(row[0]))
                            y.append(float(row[1]))
                        else:
                            return x,y
        return x,y
    
    
    def event_handler(self, event):
        '''
        Event handler for key events while viewing the plot.
        '''
        # defined key events for matplotlib plot
        if event is not None:
            if event.key in [' ']:
                if self.plot_index >= len(self.xvals) - 1:
                    self.plot_index = 0
                else:
                    self.plot_index += 1
            
            elif event.key in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
                n = int(event.key)
                self.plot_index += 2 ** n
                if self.plot_index >= len(self.xvals) - 1:
                    self.plot_index = 0
            
            elif event.key in ['0']:
                self.plot_index = self.surfaceNumber - 1
            
            elif event.key in ['r']:
                self.plot_index = 0
            
            elif event.key in ['a']:
                self.aspect = not self.aspect
            
            elif event.key in ['c']:
                self.clear_figure = not self.clear_figure
            
            elif event.key in ['f']:
                file_to_save = self.filename.replace('.srf', '.png')
                plt.savefig(file_to_save)
            
            elif event.key in ['b']:
                self.axis = not self.axis
                saveAxis = plt.axis()
            
            elif event.key in ['q']:
                plt.close()
            
            else:
                print('Pressed key "%s" is not defined!' % (event.key))
                return
            
            if self.aspect:
                self.ax1.set_aspect('equal')
                if self.multi:
                    self.ax2.set_aspect('equal')
            else:
                self.ax1.set_aspect('auto')
                if self.multi:
                    self.ax2.set_aspect('auto')
    
            if self.clear_figure:
                self.ax1.clear()
                if self.multi:
                    self.ax2.clear()
            
            if self.axis:
                plt.axis(saveAxis)
                
        
        self.ax1.plot(self.xvals[self.plot_index], self.yvals[self.plot_index], '.r-')
        self.ax1.set_title("Surface %i" % (self.plot_index + 1))
    
        if self.multi:    
            next_plot_index = (self.plot_index + int(len(self.xvals)/2)) % len(self.xvals)
            self.ax2.plot(self.xvals[next_plot_index], self.yvals[next_plot_index], '.r-')
            self.ax2.set_title("Surface %i" % (next_plot_index + 1))
                
        
        plt.xlabel("x")
        plt.ylabel("y")
        plt.draw()
    
    if __name__ == "__main__":
    	# allows to run modul also as script via command line
        plot(sys.argv[1]).plot()
