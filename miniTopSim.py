'''
Hauptprogramm von miniTopSim

Autoren:
Peter Resutik, 1126613
Roman Gehrer

'''
import math
import plot
import sys
import csv 
import numpy as np
import scipy.constants
import parameter as par
import delooping
import time
# import numpy as np


# Creates a delegate (function pointer) for given function type.
# For ease of implementation, it constructs a lambda function for it's return value.
def get_func_delegate(type):
    upper_type = type.upper();    

    if upper_type == 'COSINE':
        return lambda x: math.cos(x)
        
    if upper_type == 'DOUBLECOSINE':
        return lambda x: math.cos(x*2+math.pi)

    # We define step function as ternary function like:
    # f(x) = (x >= 0) ? 1 : 0
    # For making compliant with previous calculations,
    # we modify the step function to generate [-1, +1] for [-PI, +PI] inputs
    if upper_type == 'STEP':
        return lambda x: 2*(1 if x >= 0 else 0)-1

    # We define V-shape as triangle function which is defined as follow:
    # f(x) = |x|
    # For making compliant with previous calculations,
    # we modify the V-shape function to generate [-1, +1] for [-PI, +PI] inputs
    if upper_type == 'V-SHAPE' or upper_type == 'VSHAPE':
        return lambda x: -2*abs(x / math.pi)+1

    # For undefined types, return identity function
    return lambda x: x

def init_values(linker_grenzwert, rechter_grenzwert, delta_x):
    '''
    Diese Funktion erzeutgt zwei Numpy-Arrays (xvals und yvals).xvals geht ab dem Wert(linker_grenzwert)
    bis zum Wert(rechter_grenzwert) mit der Schrittweite delta_x
    '''

    xvals = np.linspace(linker_grenzwert,rechter_grenzwert, round((rechter_grenzwert-linker_grenzwert)/delta_x)+1)
    mask = np.less(np.abs(xvals),25)
    yvals = -50*(1 + np.cos(xvals*2*math.pi/50)) # Dies wurde in der Angabe definiert
    yvals = yvals*mask

#    func = get_func_delegate(par.INITIAL_SURFACE_TYPE)
#    func_xmin = par.FUN_XMIN
#    func_xmax = par.FUN_XMAX
#    func_period = func_xmax - func_xmin
#    func_amplitude = par.FUN_PEAK_TO_PEAK
        
#    for i in range(0, len(xvals)):
#        x = xvals[i]
#        if func_xmin <= x and x <= func_xmax:
#            yvals[i] = func_amplitude*(1 + func(x*2*math.pi/func_period)) # Dies wurde in der Angabe definiert
#        else:
#            continue
    return xvals, yvals
    
def write(file, zeitpunkt, xvals, yvals):
    '''
    Diese Funktion schreibt ins eine Datei den Zeitpunkt, Anzahl der Punkte und die x- und y- Koordinaten
    Format:
    surface: time, npoints, x-positions y-positions
    x[0] y[0]
    x[1] y[1]
    ...
    x[npoints-1] y[npoints-1]
    '''
    file.writelines('surface: {0}, {1}, x-points y-points \n'.format(zeitpunkt, len(xvals)))
    writer = csv.writer(file, lineterminator='\n', delimiter=' ')
    for i in range(0,len(xvals)):
        writer.writerow([xvals[i],yvals[i]])
    
    
def symmetrals(xvals,yvals,AP=[0,-1],EP=[0,-1]):
    '''
    Berechnung der Winkelsymmetralen von einem gegebenen Linienzug.
    Gibt die normierte Vektoren der Winkelsymmetralen, die in Druchlaufrichtung der
    Kurve betrachtet nach rechts weisen zurueck.
    
    Input: 
    xvals, yvals ... Punkte eines Kurvenzuges
    AP Winkelsymmetrale für Anfangspunkt als Liste im Fromat [x,y]
    EP Winkelsymmetrale für Endpunkt als Liste im Format [x,y]
    
    Rückgabe: 
    [xvals,yvals] Enthalten jeweils die x und y Komponenten der normierten Vektoren
    der Winkelsymmetralen
    '''
    # Herleitung der Formel für die Kurvenabschnitte
    # Kurve: k0->k1->...->kn
    # Kurvensegment links der Punkte: k1-k0, k2-k1, ... k[n-1]-k[n-2]
    # Kurvensegmente rechts der Punkte: k2-k1, k3-k2, ... x[n]-k[n-1]
    #
    #     linker Teil: (k1, k2, ... , k[n-1])-(k0, k1, ... , k[n-2])
    #                            
    #                        r1         -        r0
    #                            
    #                              
    # rechnter Teil: (k2, k3, ... ,k[n])-(k1, k2, ... , k[n-1])
    #    
    #                        r2        -         r1
    #                            
    # Durch abziehen der jeweils fehlenden Terme vom gesamten Intervall erhält
    # man die in der Gleichung unten verwendete Formel.    
    # Berechnung der Kurvenabschnitte in x Richtung
    x0=np.delete(xvals,[len(xvals)-2,len(xvals)-1])
    x1=np.delete(xvals,[0,len(xvals)-1])
    x2=np.delete(xvals,[0,1])
    xv1=x1-x0
    xv2=x2-x1
    #Berechnung der Kurvenabschnitte in y-Richtung
    y0=np.delete(yvals,[len(yvals)-2,len(yvals)-1])
    y1=np.delete(yvals,[0,len(yvals)-1])
    y2=np.delete(yvals,[0,1])
    yv1=y1-y0
    yv2=y2-y1

    #Berechung des Normalvektors des ersten Kurvenstsegments
    l1=np.sqrt(xv1**2+yv1**2)
    l1=l1+np.equal(l1,0) #Verhinderung von div-by-zero
    
    xn1=yv1/l1
    yn1=-xv1/l1
    
    l2=np.sqrt(xv2**2+yv2**2)
    l2=l2+np.equal(l2,0) #Verhinderung von div-by-zero
    
    #Normalvektor des zweiten Kurvensegments
    xn2=yv2/l2
    yn2=-xv2/l2
    
    xsym=xn1+xn2
    ysym=yn1+yn2
    
    #Berechnung der Winkelsymmetralen-Vektoren
    lsym=np.sqrt(xsym**2+ysym**2)
    lsym=lsym+np.equal(lsym,0)

    xsymn=xsym/lsym
    ysymn=ysym/lsym
    
    if AP != None:
        xsymn=np.insert(xsymn,0,AP[0])
        ysymn=np.insert(ysymn,0,AP[1])
        
    if EP != None:
        xsymn=np.append(xsymn,EP[0])
        ysymn=np.append(ysymn,EP[1])
    
    return xsymn,ysymn
    
def MovePointsByDirection(xvals,yvals,xs,ys,ds):
    '''
    Verschiebt die Punkte xvals, yvals um den Betrag ds in die gegebene Richtung xs,ys
    '''
    xvals=xvals+xs*ds
    yvals=yvals+ys*ds
    return xvals, yvals

def SputterYield(cos_theta):
    '''
    ACHTUNG: cos_theta ist der Wert des Cosinus(inneres Produkt der Einheitsvektoren)
    und NICHT der Winkel.    
    Berechnet das SputterYield für einen bestimmten Winkel mit den in der cfg-Datei
    gegebenen Parametern Y0,f,b.
    '''
    Y0=par.SPUTTER_YIELD_0
    f=par.SPUTTER_YIELD_F
    b=par.SPUTTER_YIELD_B
    return Y0*cos_theta**-f*np.exp(b*(1-1/cos_theta))
        
def SputterVelocity(xs,ys):
    '''
    Berechnet die Normalengeschwindigkeit beim Sputtern.
    Parameter:
    xs, ys Normalenrichtung der Oberfläche
    Fbeam Strahlstromdicht [Atome/(cm^2*s)] -> aus ConfigFile
    Y0, f, b Parameter des Sputter Yields -> aus ConfigFile
    N Atomdichte des Materials [Atome/cm^3] -> aus Configfile
    Ausgabe:
    vn Normalengeschwindigkeit [nm]
    '''
    Fbeam = par.BEAM_CURRENT_DENSITY/scipy.constants.e
    N = par.DENSITY
    Xspu=0; Yspu=-1 #Sputterrichtung: feste Werte aus Angabe
    cos_theta = (Xspu*xs + Yspu*ys)
    Fsput = Fbeam *SputterYield(cos_theta)*cos_theta
    vn=Fsput/N*1e7 #1e7 Umrechnung cm -> nm
    return vn

def SurfaceProcess(t,dt,xvals,yvals,file=None):
    '''
    Fuehrt abhaengig von par.ETCHING eine Bearbeitung der Oberfläche durch.
    par.ETCHING = True -> Aetzen
    par.ETCHING = False-> Sputtern
    t Gesamtzeit
    dt Zeitintervall für Berechnungsschritt
    file Wenn ein File angegeben wird, wird der Fortschritt nach jedem Druchlauf in eine
    Datei geschrieben
    '''
    for i in range(1,round(t/dt)+1):
        xs,ys = symmetrals(xvals,yvals)
        
        if par.ETCHING:
            vn=par.ETCH_RATE
        else:
            vn=SputterVelocity(xs,ys)
            
        xvals,yvals=MovePointsByDirection(xvals,yvals,xs,ys,vn*dt)
            
        if file != None:
            write(file,i*dt,xvals,yvals)
        
        if not par.NUMPY:
            xvals=list(xvals) #Umwandlung da delopping ein Liste für korrekte Funktion
            yvals=list(yvals) #braucht, wenn par.NUMPY=False
        
        xvals,yvals = delooping.deloop(xvals,yvals)
            
    return xvals,yvals
def main():
    '''
    Die Parameter werden beim Aufruf aus dem config-File abgerufen
    usage: >> miniTopSim.py <ConfigFile>
    '''
    # for UnboundLocalError, we've to define configFileName variable 
    configFileName = '' 
        
    if(len(sys.argv) == 2 ):
        configFileName = str(sys.argv[1])
    else: 
        sys.stderr.write('Error: usage: '+ sys.argv[0] + ' <filename.cfg>')
        sys.stderr.flush()
        exit(2)
    
    # Read the parameter file
    par.init()
    par.read(configFileName)
    
    # Listen xvals und yvals werden erzeugt
    xvals,yvals = init_values(par.XMIN, par.XMAX, par.DELTA_X)
        
    # Die Oberflaeche zum Zeipunkt t=0 wird geplotet
    # plotten(xvals,yvals,'bo-','Anfangszeitpunkt')
    
    # Es wird ein File erzeugt mit der Name 'basic_t_dt.srf', wobei t und dt durch 
    # die Tatsaechliche Zeit und Zeitschrittweite ersetz werden. Außerdem wird in die Datei
    # die Oberflaeche zum Zeitpunkt t=0 reingeschrieben (xvals und yvals in spalten)
    surfaceFileName = par.INITIAL_SURFACE_FILE
   
    with open(surfaceFileName,"w") as file:
        #Werte zum Zeitpunkt t=0
        write(file, 0 , xvals,yvals)
        # Start time measurement
        startTime = time.clock()
        SurfaceProcess(par.TOTAL_TIME,par.TIME_STEP,xvals,yvals,file)
        # Stop time measurement and print it
        endTime = time.clock()
        print("Calculation Time: " + str(endTime - startTime) + " seconds")
        
    plot.plot(surfaceFileName)
        
if __name__ == '__main__':
    main()  

