import sys
import os
import re
import csv
import matplotlib.pyplot as plt

x_Vals = list()
y_Vals = list()

def plot(fname):

    '''
    Plotten der Oberflaeche:

    plot(fname)

        fname is the file name e.g. trench.srf

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
    help(plot)
    global abs_filepath
    global number_of_surfaces
    global ax
    global filename

    filename = fname
    abs_filepath = get_filepath(fname)
    count_surfaces()

    number_of_surfaces = count_surfaces()
    number = 1
    
    while  get_surfacedata(number) != None:
		# get data from surfaces to plot them
        x_Vals_tmp, y_Vals_tmp = get_surfacedata(number)
        x_Vals.append(x_Vals_tmp)
        y_Vals.append(y_Vals_tmp)
        number = number + 1
        if number > number_of_surfaces:
            break

    ax = plt.subplot(111)
    event_handler(None)
    plt.connect('key_press_event', event_handler)
    plt.show()

def get_filepath(datafile_arg):
	# get the absolute path of data-file
    dir_path = os.path.dirname(os.path.abspath(__file__))
	# extend the path with the file, operating system independently 
    filepath = os.path.join(dir_path, datafile_arg)
    return filepath


def count_surfaces():
	# gets the number of surfaces that are available
    hit_count = 0
    with open(abs_filepath, "r") as file:
        for line in file:
            if re.match("surface(.*)", line):
                hit_count = hit_count + 1

    return hit_count

def get_surfacedata(surface_number):
	# parse data from xxx.srf file
	
    x = list()
    y = list()

    linenumber = 0

    with open(abs_filepath, "r") as file:
        reader = csv.reader(file, delimiter=' ')
        for line in file:
		# search for "surface" to extract data
            if re.match("surface(.*)", line): 
                linenumber = linenumber +1

            if surface_number == linenumber:
                for row in reader:
                    if not re.match("surface(.*)",row[0]):
                        x.append(float(row[0]))
                        y.append(float(row[1]))
                    else:
                        return x, y
    return x, y


def event_handler(event):
	# defined key events for matplotlib plot 

    global plot_index
    global aspect
    global clear_figure
    global axis
    global saveAxis

    if event is None:
        plot_index = 0
        aspect = 0
        clear_figure = 1
        axis = False
        saveAxis = [-60, 60 -120, 20]

    else:
        if event.key in [' ']:
            if plot_index >= len(x_Vals) - 1:
                plot_index = 0
            else:
                plot_index += 1

        elif event.key in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
            n = int(event.key)
            plot_index += 2 ** n
            if plot_index >= len(x_Vals) - 1:
                plot_index = 0

        elif event.key in ['0']:
            plot_index = number_of_surfaces - 1

        elif event.key in ['r']:
            plot_index = 0

        elif event.key in ['a']:
            aspect = not aspect

        elif event.key in ['c']:
            clear_figure = not clear_figure

        elif event.key in ['f']:
            file_to_save = filename.replace('.srf', '.png')
            plt.savefig(file_to_save)

        elif event.key in ['b']:
            axis = not axis
            saveAxis = plt.axis()

        elif event.key in ['q']:
            plt.close()

        else:
            print('Pressed key "%s" is not defined!' % (event.key))
            return

    if aspect:
        ax.set_aspect('equal')
    else:
        ax.set_aspect('auto')

    if clear_figure:
        ax.clear()

    if axis:
        plt.axis(saveAxis)#([-60, 60, -120, 20])

    ax.plot(x_Vals[plot_index], y_Vals[plot_index], '.r-')
    ax.set_title("Surface %i" % (plot_index+1))
    plt.xlabel("x")
    plt.ylabel("y")
    plt.draw()

if __name__ == "__main__":
	# allows to run modul also as script via command line
    fname = sys.argv[1]
    plot(fname)
