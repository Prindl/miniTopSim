#  adaptive_grid.py
#
#  Lukas Gosch
#  1326060
#

import numpy as np
from scipy import interpolate
import parameter as par
import sys
'''
interpolation_typ: "linear", "quadratic", "cubic"

Falls die Segmentlänge zwischen 2 Punkten den Wert par.MAX_SEGLEN + Toleranz überschreitet, wird ein neuer Punkt
hinzugefügt. Wird der Abstand zwischen linkem und rechtem Nachbarpunkt eines Punktes kleiner als par.MAX_SEGLEN - Toleranz
dann wird der Punkt entfernt soweit nicht das Winkelkriterium beim Entfernen verletzt werden würde.
Weiters wird, falls der Winkel zwischen Oberflächennormalen benachbarter Segmente größer als par.MAX_ANGLE ist,
zusätzliche Knoten mit identen Koordinaten aber unterschiedlichen Winkelsymmetralen eingefügt, bis das Winkelkriterium
nicht mehr verletzt wird.
'''
def adapt(surface, interpolation_type="linear"):
    xs, ys = anglebisect(surface.xvals, surface.yvals)

    tolerance = par.MAX_SEGLEN * 0.05 #tolerance of +-5%

    #list because nparrays are not mutable
    xlist = list(surface.xvals)
    ylist = list(surface.yvals)

    xslist = list(xs)
    yslist = list(ys)

    f = interpolate.interp1d(surface.xvals, surface.yvals, interpolation_type) #interpolated function

    #Erste Schleife prüft Abstandskriterium
    i = 0
    while i != len(xlist)-1: #len-1 sodass immer ein rechter Nachbar existiert
        #falls x-Werte nicht monoton steigend
        if xlist[i] > xlist[i+1]:
            print("Error Adaptives Gitter: x-Werte sind nicht monoton steigend!")
            #sys.exit() Auskommentiert, da adapt() mit falschen (nicht monotonen) x-Werten aufgerufen wird, was
            #derzeit noch bei jeder Konfiguration im Laufe der Zeitschritte passiert

        #Falls Segmentlänge zu lange
        if checkDistanceBiggerMAX((xlist[i], ylist[i]), (xlist[i+1], ylist[i+1]), tolerance) :
            #Füge Knoten hinzu
            xlist, ylist, xslist, yslist = insertPoint(i, f, xlist, ylist, xslist, yslist, surface)
            continue #erhöhe i nicht um 1 sodass das Längenkriterium für die Länge zwischen dem alten Punkt und dem neuen Punkt überprüft wird

        if i > 0: #da bei i=0 kein Linker Nachbar existiert
            #Entferne Knoten falls Länge von linken zu rechten Nachbarn zu kurz und Winkelkriterium nicht verletzt wird
            #Hier können noch keine Dublikate existieren da diese erst nach der Schleife in der wir uns jetzt befinden
            #eingefügt werden
            if checkDistanceSmallerMAX((xlist[i-1], ylist[i-1]), (xlist[i+1], ylist[i+1]), tolerance):
                if i < (len(xlist) - 2):
                    check1 = checkAngleCriterium([xlist[i-1], xlist[i+1], xlist[i+2]], [ylist[i-1], ylist[i+1], ylist[i+2]], [xslist[i-1], xslist[i+1], xslist[i+2]], [yslist[i-1], yslist[i+1], yslist[i+2]])
                else:
                    check1 = True #vorletzter rechter Randpunkt, desshalb kann rechts das Winkelkriterium nicht verletzt werden
                if i > 1:
                    check2 = checkAngleCriterium([xlist[i-2], xlist[i-1], xlist[i+1]], [ylist[i-2], ylist[i-1], ylist[i+1]], [xslist[i-2], xslist[i-1], xslist[i+1]], [yslist[i-2], yslist[i-1], yslist[i+1]])
                else:
                    check2 = True #vorletzter linker Randpunkt, desshalb kann links das Winkelkriterium nicht verletzt werden

                if check1 and check2:
                    xlist, ylist, xslist, yslist = removePoint(i, xlist, ylist, xslist, yslist)
                    i -= 1 #da ein Punkt entfernt wird und die Kriterien nun für den vorherigen Punkt relativ zum rechten Nachbarn geprüft werden müssen
                    continue

        i += 1 #wenn auf alle Kriterien geprüft wurde, kann zum nächsten Punkt gesprungen werden

    #2. Schleife, wenn die Knoten aufgrund des Abstandskriteriums geprüft und hergerichtet wurden,
    #wird geprüft ob zusätzliche Knoten aufgrund des Winkelkriteriums eingefügt werden müssen
    i = 0
    while i != len(xlist) - 1:
        if i > 0:
            #Falls Winkelkriterium nicht erfüllt wird, füge neue Knoten mit neuen Winkelsymmetralen ein
            if not checkAngleCriteriumIncludingDublicates(i, xlist, ylist, xslist, yslist):
                xlist, ylist, xslist, yslist = insertPointsSameCoordinates(i, xlist, ylist, xslist, yslist)
                continue #erhöhe i nicht um 1 da das Winkelkriterium für die neu hinzugefügten Punkte ebenfalls geprüft werden muss
        i += 1
    surface.xvals = np.array(xlist)
    surface.yvals = np.array(ylist)
    surface.xs = np.array(xslist)
    surface.ys = np.array(yslist)

'''
Entfernt Punkt an Stelle i und berechne die Konsequenzen für die Winkelsymmetralen der umliegenden Punkte
'''
def removePoint(i, xlist, ylist, xslist, yslist):
    if checkDuplicate(xlist[i-1:i+2], ylist[i-1:i+2]):
        print("Error: removePoint mit Duplikaten in der Punktliste aufgerufen")
        sys.exit()

    xlist.remove(xlist[i])
    ylist.pop(i) #pop da remove den gleichen value löscht welcher allerdings doppelt vorkommen kann
    xslist.pop(i)
    yslist.pop(i)

    #Berechne neuen Normalvektor auf das neue Segmente
    n_new = calcNormal(i, xlist, ylist)

    #Ersetze alte mit neuen Winkelsymmetralen die mit dem neuen Normalvektor auf das neu entstandende Segment berechnet
    #wurden, nur falls nicht der Punkt neben den Randpunkten entfernt wurde
    if i > 1:
        n1 = calcNormal(i-1, xlist, ylist)
        sym1 = calcSymmetral(n1, n_new)
        xslist[i-1] = sym1[0]
        yslist[i-1] = sym1[1]

    if i < (len(xlist) - 2):
        n2 = calcNormal(i+1, xlist, ylist)
        sym2 = calcSymmetral(n_new, n2)
        xslist[i] = sym2[0]
        yslist[i] = sym2[1]

    return xlist, ylist, xslist, yslist

'''
Fügt Knoten zwischen i und i+1 ein und berechnet zugehörige Winkelsymmetralen. P(i) und P(i+1) müssen unterschiedliche
Koordinaten besitzen.
'''
def insertPoint(i, f, xlist, ylist, xslist, yslist, surface):
    if checkDuplicate(xlist[i:i+2], ylist[i:i+2]):
        print("Error: insertPoint mit Knoten mit selben Koordinaten aufgerufen")
        sys.exit()

    xlist.insert(i+1, xlist[i] + (xlist[i+1] - xlist[i]) / 2 ) #inserts xvalue between i and i+1
    ylist.insert(i+1, f(xlist[i+1])) #inserts new interpolated yvalue to new xvalue

    #Berechne neue Winkelsymmetralen (benötigt für hinzugefügten Punkt sowie für die Nachbarn)
    xs_temp, ys_temp = anglebisect(xlist, ylist)
    xslist = list(xs_temp)
    yslist = list(ys_temp)
    return xlist, ylist, xslist, yslist
    
    
def anglebisect(xvals, yvals, AP=[0,-1], EP=[0,-1]):
    '''
          
    Calculates the anglebisectors of a curve, as unit vectors.
    
    Input(optional):
    AP anglebisector of the starting point as [x,y]
    EP anglebisector of the end point as [x,y]
    
    Usage:
    >>>xs, ys = anglebisect(xvals, yvals)
    calculates the anglebisectors with the surfaces x,y - values 

    '''
    # Herleitung der Formel für die Kurvenabschnitte
    # Kurve: k0->k1->...->kn
    # Kurvensegment links der Punkte: k1-k0, k2-k1, ... k[n-1]-k[n-2]
    # Kurvensegmente rechts der Punkte: k2-k1, k3-k2, ... k[n]-k[n-1]
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
    x0 = np.array(xvals[:-2])
    x1 = np.array(xvals[1:-1])
    x2 = np.array(xvals[2:])
    xv1 = x1 - x0
    xv2 = x2 - x1
    #Berechnung der Kurvenabschnitte in y-Richtung
    y0 = np.array(yvals[:-2])
    y1 = np.array(yvals[1:-1])
    y2 = np.array(yvals[2:])
    yv1 = y1-y0
    yv2 = y2-y1

    l1 = np.sqrt(xv1**2 + yv1**2)
    #Berechung des Normalvektors des ersten Kurvenstsegments
    xn1 = yv1/l1
    yn1 = -xv1/l1
    
    l2 = np.sqrt(xv2**2 + yv2**2)    
    #Normalvektor des zweiten Kurvensegments
    xn2 = yv2/l2
    yn2 = -xv2/l2
    
    xsym = xn1 + xn2
    ysym = yn1 + yn2
    
    #Berechnung der Winkelsymmetralen-Vektoren
    lsym = np.sqrt(xsym**2 + ysym**2)

    xsymn = xsym/lsym
    ysymn = ysym/lsym
    
    xsymn = np.insert(xsymn,0,AP[0])
    ysymn = np.insert(ysymn,0,AP[1])
        
    xsymn = np.append(xsymn,EP[0])
    ysymn = np.append(ysymn,EP[1])

    return xsymn, ysymn


'''
Fügt zu einem Knoten an der Stelle i zwei weitere mit unterschiedlichen Winkelsymmetralen hinzu
'''
def insertPointsSameCoordinates(i, xlist, ylist, xslist, yslist):

    #Falls Duplikate in der Liste vorkommen muss die Winkelsymmetralenberechnung anders durchgeführt werden
    #da keine Strecke und dadurch kein Normalvektor zwischen zwei identen Punkten existiert
    #Wenn ich von links oder rechts spreche, dann davon, dass sich die dazugehören Punkte
    #links oder rechts in der Punkteliste (relativ zum Punkt an der Stelle i) befinden oder eingefügt werden sollen
    if checkDuplicate(xlist[i-1 : i+2], ylist[i-1 : i+2]):
        #Knoten links und rechts vom aktuellen Knoten ein Duplikat?
        if checkDuplicate(xlist[i-1:i+1], ylist[i-1:i+1]) and checkDuplicate(xlist[i:i+2], ylist[i:i+2]):
            n2 = (xslist[i-1], yslist[i-1])
            n1 = (xslist[i+1], yslist[i+1])

        #Knoten links vom aktuellen Knoten ein Duplikat?
        elif checkDuplicate(xlist[i-1:i+1], ylist[i-1:i+1]):
            j = 0
            while checkDuplicate(xlist[i+j-2:i+j], ylist[i+j-2:i+j]):
                j-=1
            #Erster linker nicht Dublikatpunkt hat Koordinaten P(i+j-2)
            secondDerivativeY = calculateSignSecondDerivative(1, [xlist[i+j-2], xlist[i], xlist[i+1]], [ylist[i+j-2], ylist[i], ylist[i+1]])
            if secondDerivativeY < 0:
                #Falls 2. Ableitung < 0 berechnet sich die neue rechte Winkelsymmetrale aus dem Normalvektor der Strecke zum
                #ersten links auftauchenden nicht identen Punktes und dem jetzigen Punkt
                n1 = calcNormal(i+j-1, xlist, ylist)
                #Die neue linke Winkelsymmetrale ist die Winkelsymmetrale zwischen der Winkelsymmetrale des linken (identen)
                #Punktes und des jetzigen Punktes
                n2 = (xslist[i-1], yslist[i-1])
            else:
                #Falls die 2. Ableitung > 0 berechnet sich die neue rechte Winkelsymmetrale aus dem Normalvektor der Strecke
                #zum rechten Punkt (und dem jetzigen Punkt) und die neue linke Winkelsymmetrale ist die Winkelsymmetrale
                #zwischen den Winkelsymmetralen des jetzigen Punktes und des linken (identen) Punkt
                n1 = calcNormal(i+1, xlist, ylist)
                n2 = (xslist[i-1], yslist[i-1])

        #Knoten rechts vom aktuellen Knoten ein Duplikat?
        elif checkDuplicate(xlist[i:i+2], ylist[i:i+2]):

            j = 0
            while checkDuplicate(xlist[i+j+1:i+j+3], ylist[i+j+1:i+j+3]):
                j+=1
            #Erster rechter nicht Dublikatpunkt hat Koordinaten P(i+j+2)
            secondDerivativeY = calculateSignSecondDerivative(1, [xlist[i-1], xlist[i], xlist[i+j+2]], [ylist[i-1], ylist[i], ylist[i+j+2]])
            if secondDerivativeY < 0:
                #Falls 2. Ableitung < 0, berechnet sich die neue linke Winkelsymmetrale aus dem Normalvektor der Strecke zum ersten
                #rechts auftauchenden nicht identen Punkt und die neue rechte Winkelsymmetrale als die Winkelsymmetrale
                #zwischen den Winkelsymmetralen des jetzigen Punktes und des rechten (identen) Punktes
                n2 = calcNormal(i+j+2, xlist, ylist)
                n1 = (xslist[i+1], yslist[i+1])
            else:
                #Falls 2. Ableitung > 0, berechnet sich die neue linke Winkelsymmetrale aus dem Normalvektor der Strecke
                #zum linken nicht identen Punkt und aus der Winkelsymmetrale des jetzigen Punktes
                n2 = calcNormal(i, xlist, ylist)
                #Die rechte Winkelsymmetrale, ist die Winkelsymmetrale zwischen der Winkelsymmetrale des jetzigen Punktes
                #und des rechten identen Punktes
                n1 = (xslist[i+1], yslist[i+1])
        #n1 und n2 wurden entsprechend der Kommentare oben gewählt um die richten neuen rechten/linken Winkelsymmetralen zu
        #den neu einzufügenden Punkten zu berechnen
        rightSym = calcSymmetral(n1, (xslist[i], yslist[i]))
        leftSym = calcSymmetral((xslist[i], yslist[i]), n2)
    else:
        #Berechne Winkelsymmteralen der neu einzufügenden Knoten mit den normalen Oberflächennormalen
        n1 = calcNormal(i, xlist, ylist)
        n2 = calcNormal(i+1, xlist, ylist)

        #Vorzeichen der 2. Ableitung definiert ob die Winkelsymmetrale des neuen linken/rechten Punktes
        #jeweils mit linkem oder rechtem Normalvektor berechnet wird
        dy1 = (ylist[i] - ylist[i-1]) / (xlist[i] - xlist[i-1])
        dy2 = (ylist[i+1] - ylist[i]) / (xlist[i+1] - xlist[i])
        if dy1 >= 0:
            if (dy1 - dy2) > 0:
                secondDerivativeY = -1
            else:
                secondDerivativeY = 1
        if dy1 < 0:
            if (dy2 - dy1) > 0:
                secondDerivativeY = 1
            else:
                secondDerivativeY = -1

        if secondDerivativeY <= 0 :
            leftSym = calcSymmetral((xslist[i], yslist[i]), n2)
            rightSym = calcSymmetral(n1, (xslist[i], yslist[i]))
        if secondDerivativeY > 0 :
            leftSym = calcSymmetral(n1, (xslist[i], yslist[i]))
            rightSym = calcSymmetral((xslist[i], yslist[i]), n2)

    #Add Points
    xlist.insert(i+1, xlist[i])
    ylist.insert(i+1, ylist[i])
    xslist.insert(i+1, rightSym[0])
    yslist.insert(i+1, rightSym[1])

    xlist.insert(i, xlist[i])
    ylist.insert(i, ylist[i])
    xslist.insert(i, leftSym[0])
    yslist.insert(i, leftSym[1])

    return xlist, ylist, xslist, yslist

'''
Berechnet Vorzeichen der Zweiten Ableitung
'''
def calculateSignSecondDerivative(i, xlist, ylist):
    dy1 = (ylist[i] - ylist[i-1]) / (xlist[i] - xlist[i-1])
    dy2 = (ylist[i+1] - ylist[i]) / (xlist[i+1] - xlist[i])
    if dy1 >= 0:
        if (dy1 - dy2) > 0:
            secondDerivativeY = -1
        else:
            secondDerivativeY = 1
    if dy1 < 0:
        if (dy2 - dy1) > 0:
            secondDerivativeY = 1
        else:
            secondDerivativeY = -1

    return secondDerivativeY


'''
p1 = (x1, y2) Punkt 1 als Tupel
p2 = (x2, y2) Punkt 2 als Tupel
return true falls Segmentlänger größer MAX_SEGLEN + Toleranzbereich
'''
def checkDistanceBiggerMAX(p1, p2, tolerance):
    dist = calcDistance(p1, p2)
    return dist > (par.MAX_SEGLEN + tolerance)

'''
p1 = (x1, y2) Punkt 1 als Tupel
p2 = (x2, y2) Punkt 2 als Tupel
return true falls Segmentlänger kleiner MAX_SEGLEN - Toleranzbereich
'''
def checkDistanceSmallerMAX(p1, p2, tolerance):
    dist = calcDistance(p1, p2)
    return dist < (par.MAX_SEGLEN - tolerance)

'''
p1 = (x1, y2) Punkt 1 als Tupel
p2 = (x2, y2) Punkt 2 als Tupel

Berechnet den Abstand des Punktes p2 zu p1
'''
def calcDistance(p1, p2):
    return np.sqrt(np.square(p2[0] - p1[0]) + np.square(p2[1] - p1[1]))

'''
Überprüft ob Winkelkriterium nicht verletzt wird.

Winkelkriterium: Winkel zwischen Oberflächennormalen benachbarter Segmente größer als MAX_ANGLE
definiert in der parameter.db, die Berechnung ist abhängig davon es sich bei den Nachbarpunkten um Knoten mit
unterschiedlichen Koordinaten oder um Knoten mit identen Koordinaten handelt. Diese Version der Methode darf
nur ohne Dublikate aufgerufen werden.

return true: Winkel zwischen Oberflächennormalen <= par.MAX_ANGLE
'''
def checkAngleCriterium(xlist, ylist, xslist, yslist):
    #Falls Duplikate in der Liste vorkommen muss das Winkelkriterium anders geprüft werden
    if checkDuplicate(xlist, ylist):
        print("Error: Wrong Call of checkAngleCriterium")
        sys.exit()
        #return checkAngleCriteriumIncludingDublicates(1, xlist, ylist, xslist, yslist)

    n1 = calcNormal(1, xlist, ylist)
    n2 = calcNormal(2, xlist, ylist)

    if calcAngle(n1, n2) > par.MAX_ANGLE:
        return False
    return True

'''
Überprüft ob Winkelkriterium nicht verletzt wird.

Winkelkriterium: Winkel zwischen Oberflächennormalen benachbarter Segmente größer als MAX_ANGLE
definiert in der parameter.db, die Berechnung ist abhängig davon es sich bei den Nachbarpunkten um Knoten mit
unterschiedlichen Koordinaten oder um Knoten mit identen Koordinaten handelt. Falls es sich bei den Nachbarknoten
um Knoten mit identen Koordinaten handelt kann keine Oberflächennormale (der Strecke 0 zwischen den Knoten) berechnet
werden und es wird stattdessen die Winkelsymmetrale des Nachbarpunktes herangezogen.

return true: Winkel zwischen Oberflächennormalen <= par.MAX_ANGLE
'''
def checkAngleCriteriumIncludingDublicates(i, xlist, ylist, xslist, yslist):

    if (len(xlist)-1) == i: #letzter Punkt
        return True

    #Falls Duplikate in der Liste vorkommen muss das Winkelkriterium anders geprüft werden
    if checkDuplicate(xlist[i-1 : i+2], ylist[i-1 : i+2]):
        #Knoten links und rechts vom aktuellen Knoten ein Duplikat?
        if checkDuplicate(xlist[i-1:i+1], ylist[i-1:i+1]) and checkDuplicate(xlist[i:i+2], ylist[i:i+2]):
            n1 = (xslist[i-1], yslist[i-1])
            n2 = (xslist[i], yslist[i])
        #Knoten links vom aktuellen Knoten ein Duplikat?
        elif checkDuplicate(xlist[i-1:i+1], ylist[i-1:i+1]):
            n1 = (xslist[i-1], yslist[i-1])
            n2 = (xslist[i], yslist[i])
        #Knoten rechts vom aktuellen Knoten ein Duplikat?
        elif checkDuplicate(xlist[i:i+2], ylist[i:i+2]):
            n1 = (xslist[i], yslist[i])
            n2 = (xslist[i+1], yslist[i+1])

        if (2 * calcAngle(n1, n2)) > par.MAX_ANGLE:
            return False
        return True

    else:
        #Normal berechnen mit Oberflächennormalen
        n1 = calcNormal(i, xlist, ylist)
        n2 = calcNormal(i+1, xlist, ylist)

    if calcAngle(n1, n2) > par.MAX_ANGLE:
        return False
    return True

'''
Prüft ob in der Liste zwei gleiche Punkte (gleiche Koordinaten) aufeinanderfolgen und liefert "True" zurück falls dies vorkommt
'''
def checkDuplicate(xlist, ylist):
    for i in range(0, len(xlist)-1):
        if np.round(xlist[i+1] - xlist[i], 5) == 0 and np.round(ylist[i+1] - ylist[i], 5) == 0 :
            return True
    return False

'''
returns Winkel den die übergebenen Vektoren einschließen
'''
def calcAngle(n1, n2):
    if round(n1[0] - n2[0], 5) == 0 and round(n1[1] - n2[1], 5) == 0:
        return 0
    angle = np.rad2deg(np.arccos(np.inner(n1, n2) / (np.linalg.norm(n1)*np.linalg.norm(n2))))
    return angle

'''
Liefert den normierten Normalvektor n = (dy, -dx) auf ein Segment P(i-1) bis P(i) zurück
'''
def calcNormal(i, xlist, ylist):
    xv1=xlist[i]-xlist[i-1]
    yv1=ylist[i]-ylist[i-1]
    l1=np.sqrt(xv1**2+yv1**2)

    xn1=yv1/l1
    yn1=-xv1/l1

    return [xn1, yn1]

'''
Liefert die normierte Winkelsymmetrale für zwei gegebene Vektoren zurück
'''
def calcSymmetral(n1, n2):
    xs = n1[0] + n2[0]
    ys = n1[1] + n2[1]

    ls=np.sqrt(xs**2+ys**2)

    xs=xs/ls
    ys=ys/ls

    return [xs, ys]
