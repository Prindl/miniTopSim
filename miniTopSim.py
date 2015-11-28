# Grundversion von miniTopSim

# Peter Resutik
# 1126613

import math
import plot
import sys
import csv 
import matplotlib.pyplot as plt
# import numpy as np


def init_values(linke_grenzwert, rechte_grenzwert):
    '''
    Diese Funktion erzeutgt zwei Listen (xvals und yvals).Die Liste xvals geht ab dem Wert(linke_grenzwert)
    bis zum Wert(rechte_grenzwert) mit der Schrittweite delta_x = 1 [nm]
    '''
    lst = list(range(linke_grenzwert, rechte_grenzwert + 1))
    xvals = [float(i) for i in lst]
    yvals = [0.0] * len(xvals)
    for i in range(0, len(xvals)):
        if abs(xvals[i]) < 25: 
            yvals[i] = -50*(1 + math.cos(xvals[i]*2*math.pi/50)) # Dies wurde in der Angabe definiert
        else:
            continue
    return xvals, yvals

# DIESE FUNKTION IST NICHT NOETIG, DA ICH DIE FUNKTION plot VON DEM MODULE PLOT (SIEHE OBEN) VERWENDE (AUTOR: Markus Piller)
# def plotten(xvals,yvals, typ, label):
#    '''
#    Die Eigenschaften des Plots werden eingestellt (labels, title, axis, typ)
#    '''
#    plt.xlabel('x in [nm]')
#    plt.ylabel('y in [nm]')
#    plt.title('Isotropes Aetzen')
#    plt.axis([-60, 60, -120, 20])
#    plt.grid(True)
#    plt.plot(xvals, yvals, typ, label=label) # unter dem typ wird verstanden die Farbe und die Form der Kurve z.B. 'bo-'
    
def write(file, zeitpunkt, xvals, yvals):
    '''
    Diese Funktion schreibt ins eine Datei den Zeitpunkt, Anzahl der Punkte und die x- und y- Koordinaten
    '''
    file.writelines('surface: {0}, {1}, x-points y-points \n'.format(zeitpunkt, len(xvals)))
    writer = csv.writer(file, lineterminator='\n', delimiter=' ')
    writer.writerows(zip(xvals,yvals))

def aetzen(file, t, dt, xvals, yvals):
    '''
    Mit hilfe dieser Funktion wird entlang der Winkelsymmetrale benachbarter Segmente ins Material geaetzt,
    wobei die Zeit t ueber die geaetzt wird und die Zeitschrittweite dt uebergegeben werden
    '''
    # Die Listen xvals2 und yvals2 nach dem aetzen werden erzeugt
    xvals2,yvals2 = init_values(-50,50)
    # yvals2 muss ueberschrieben werden (es wird auf allen Stellen in der Liste der Wert -dt reingeschrieben)
    yvals2 = [float(-dt)] * 101
    
    # t/dt - Anzahl der Aetzschritten
    for j in range(0,int(t/dt)):
        # Die Winkelsymetrale fuer jeden punkt wird berechnet und nomiert, diese wird danach
        # von dem punkt abgezogen bzw noch davor mit der Zeitschrittweite multipliziert
        for i in range(1,len(xvals)-1):
            # Die Vektoren werden erzeugt (x und y komponente)
            abx=xvals[i-1]-xvals[i] # Vektor ab (x-komponente)
            aby=yvals[i-1]-yvals[i]
            acx=xvals[i+1]-xvals[i]
            acy=yvals[i+1]-yvals[i]
            # danach normiert (durch die laengen dividiert)
            lab=math.sqrt(abx**2+aby**2) # Laenge des ab Vektors
            lac=math.sqrt(acx**2+acy**2)
            # und zusammen addiert (somit wird die Winkelsymmetrale erzeugt (dise wird auch normiert))
            abn=abx/lab+acx/lac # normierte ab Vektor
            acn=aby/lab+acy/lac
            lws=math.sqrt(abn**2+acn**2) # Winkelsymmetrale (noch nicht normiert)
            # und dann wird geaetzt 
            if lws==0:
                xvals2[i]=xvals[i]
                yvals2[i]=yvals[i]-dt
            # von dem ac Vektor wird ein senkrechter Vektor erzeugt (siehe -aby und abx) und diese im In-Produkt mit 
            # der Winkelsymmetrale mupltipliziert. Dadurch wird entschieden auf welcher Seite der Material 
            # (der Senkrechte Vektor(-aby, abx)zeigt naemlich immer ins Material) und auf welcher Seite der Aetz-Stoff ist
            elif (-aby*(abn/lws)+(abx*(acn/lws)))>0: 
                xvals2[i]=xvals[i]+(abn/lws)*dt
                yvals2[i]=yvals[i]+(acn/lws)*dt
            else:
                xvals2[i]=xvals[i]+(abn/lws)*(-1)*dt
                yvals2[i]=yvals[i]+(acn/lws)*(-1)*dt
        
        # nach jedem Aetzschritt werden die Listen xvals2 und yvals2 in die File (basic_t_dt.srf) geschreiben
        write(file, j+dt, xvals2,yvals2)
        # Die listen werden fuer die neue Iteration vorbereitet
        xvals=xvals2[:]
        yvals=yvals2[:]
        yvals2 = [-(j+2.0)] * len(yvals)
    return xvals,yvals
    
    
def main():
    '''
    Es handelt sich um Isotropes Aetzen einer Oberflaeche entlang der Winkelsymmetrale (1nm/s):
    Es werden zwei Parameter ueber die command line uebergegeben, die Zeit t ueber die 
    geaetzt wird und die Zeitschrittweite dt.
    
    usage: >> miniTopSim.py t dt
    
    Außerdem werden die Koordinaten ins eine Datei geschrieben in dem Format:
    
    surface: time, npoints, x-positions y-positions
    x[0] y[0]
    x[1] y[1]
    ...
    x[npoints-1] y[npoints-1]
    
    '''
    
    # Falls weniger oder mehr als drei parameter uebergegeben werden,
    # kommt eine Fehlermeldung die Die richtige Eingabe deutet
    if(len(sys.argv) == 3 ):
        t = int(sys.argv[1]) 
        dt = int(sys.argv[2])
    else: 
        sys.stderr.write('Error: usage: '+ sys.argv[0] + ' <t> <dt>')
        sys.stderr.flush()
        exit(2)
        
    # Listen xvals und yvals werden erzeugt
    xvals,yvals = init_values(-50,50)
        
    # Die Oberflaeche zum Zeipunkt t=0 wird geplotet
    # plotten(xvals,yvals,'bo-','Anfangszeitpunkt')
    
    # Es wird ein File erzeugt mit der Name 'basic_t_dt.srf', wobei t und dt durch 
    # die Tatsaechliche Zeit und Zeitschrittweite ersetz werden. Außerdem wird in die Datei
    # die Oberflaeche zum Zeitpunkt t=0 reingeschrieben (xvals und yvals in spalten)
    file = open('basic_{0}_{1}.srf'.format(sys.argv[1],sys.argv[2]),"w")
    write(file, 0 , xvals,yvals)
    
    aetzen(file, t, dt, xvals, yvals)
    
    file.close()
    
    # Die Oberflaeche zum Endzeitpunkt wird geplotet
    # plotten(xvals,yvals,'ro-','Endzeitpunkt')
    
    fname = 'basic_{0}_{1}.srf'.format(sys.argv[1],sys.argv[2])
    plot.plot(fname)
        
    # plt.legend()
    # plt.show()

if __name__ == '__main__':
    main()
