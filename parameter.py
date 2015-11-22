# -*- coding: utf-8 -*-
'''
Modul zum Laden einer Parameter Datenbank namens parameters.db

PARAMETER ConfigParser Objekt der Parameter
COMMENT   ConfigParser Objekt der Kommentare/Erklärungen
CONDITION ConfigParser Objekt der Bedinungen



init() lädt die Datenbank namens parameters.db

read(Datei) lädt Paramter aus der Datei
bei nicht übereinstimmen des Typs gibt es einen Error und das Programm wird beendet

toDict() gibt ein Dictionary mit den keys und den werten aus PARAMETER zurück

@author:Michael Hahn e1125097@student.tuwien.ac.at
'''

import configparser
import sys



#hilfs Config objekte
PARAMETER = configparser.ConfigParser()
CONDITION = configparser.ConfigParser()
COMMENT   = configparser.ConfigParser()
PAR_IN    = configparser.ConfigParser()


#Typabfrage des Parameters Rückgabewert ist der Typ als String
#Vorher float dann bool, weil wenn zahl mit 0 enthält würde bool ausschlagen
def checktypeparameter(section,key):
    #versucht ob der angegebene string ein float ist    
    try:
        PARAMETER.getfloat(section,key)
        typ='float'
    except ValueError:
        #wenn es kein float ist wird überprüft ob es eine boolsche Variable ist
        try: 
            PARAMETER.getboolean(section,key)
            typ='bool'
        #ansonst ist es ein string
        except ValueError:
            typ='string'
    return typ
    
def checktypepar_in(section,key):
    try:
        PAR_IN.getfloat(section,key)
        typ='float'
    except ValueError:
        try:
            PAR_IN.getboolean(section,key)
            typ='bool'
        except ValueError:
            typ='string'
    return typ    

    
def init():
    #parameters.db einlesen
    PAR_DEFAULT = configparser.ConfigParser()
    PAR_DEFAULT.read('parameters.db')
    #Schleife über alle sections
    for section in PAR_DEFAULT:
        
        #erstellen der Sections in den config objekten
        PARAMETER[section]={}
        CONDITION[section]={}
        COMMENT[section]={}
        #schleife über alle Parameter in der Section
        for key in PAR_DEFAULT[section]:
            #Auslesen des Tupels aus dem strin und zuteilung zu den Config objekten
            tupel=eval(PAR_DEFAULT.get(section,key),{},{})
            PARAMETER[section][key]=str(tupel[0])
            CONDITION[section][key]=str(tupel[1])
            #Überprüfung ob die Bedingung richtig ist            
            try:
                CONDITION.getboolean(section,key)
            except ValueError:
                if(CONDITION[section][key].lower() == 'none'):
                    CONDITION[section][key]='True'
                else:
                    error='Type of condition '+key+' is not correct'
                    sys.exit(error)
            COMMENT[section][key]=str(tupel[2])
            
def read(Datei):
    #Datei einlesen
    PAR_IN.read(Datei)
    #Iteration über alle Sections und Keys
    for section in PARAMETER:
        for key in PARAMETER[section]:
            #Abfrage ob die Eingelesene section und der key vorhanden sind und abfrage ob die Bedingung erfüllt ist
            if (section in PAR_IN) and (key in PAR_IN[section]) and CONDITION.getboolean(section,key):
                #Abfrage ob die Typen übereinstimmen
                if checktypepar_in(section,key) is checktypeparameter(section,key):
                    PARAMETER[section][key]=PAR_IN[section][key]
                else:
                    #Beendigung des Programms wenn der Typ nich übereinstimmt
                    error='Type of '+key+' does not match with type in parameters.db'
                    sys.exit(error)
    PAR_IN.clear()
    
def toDict():
    dictionary={}
    for section in PARAMETER:
        for key in PARAMETER[section]:
            dictionary[key]=PARAMETER.get(section,key)
    return dictionary
