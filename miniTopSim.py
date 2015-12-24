'''
Hauptprogramm von miniTopSim

Autoren:
Peter Resutik, 1126613
Roman Gehrer

'''
from sys import stderr, argv
import parameter as par
from plot import plot as Plot
from surface import surface as Surface

    
def main():
    '''
    Die Parameter werden beim Aufruf aus dem config-Files abgerufen
    usage: >> miniTopSim.py <ConfigFiles...>
    '''
    if(len(argv) > 1 ):
        configFileNames = argv[1:]
    else: 
        stderr.write('Error: usage: '+ argv[0] + ' <filename.cfg>')
        stderr.flush()
        exit(2)
    
    # Read the parameter file
    par.init()
    print('Configuration files:\n{0}\n'.format(configFileNames))
    for configFiles in configFileNames:
        par.read(configFiles)
        surface = Surface()
        with open(surface.get_surfaceFile(), "w") as file:
            #initial values
            surface.write(file, 0)
            total_time = par.TOTAL_TIME
            dt = par.TIME_STEP
            time =  1 #np.arange(initialTime, total_time + dt, dt)
            
            while time <= total_time:
                surface.process(time, dt)
                time += dt
                surface.write(file, time * dt)
        plot = Plot(surface.get_surfaceFile())
        plot.plot()
        
        
if __name__ == '__main__':
    main()  
