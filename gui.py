# -*- coding: utf-8 -*-
"""
@author: Ebmer Gerald, Lukas Pechhacker
"""

import sys, os, PySide, configparser
from ast import literal_eval
from PySide import QtGui, QtCore
from pydoc import locate
import parameter as IOParameter

class Parameter:
    def __init__(self,name,value,comment,condition):
        self.name = name
        self.value = value
        self.comment = comment
        self.condition = condition
        
    def getName(self):
        return self.name
        
    def getValue(self):
        return self.value
        
    def getComment(self):
        return self.comment
        
    def getCondition(self):
        return self.condition
        
    def setValue(self,value):
        self.value = value
        
class Section:
    def __init__(self,name):
        self.name = name
        self.parameters = []
    
    def addParameter(self,parameter):
        self.parameters.append(parameter)
        
    def getParameters(self):
        return self.parameters
        
    def getName(self):
        return self.name

    def getParameter(self,name):
        for parameter in self.parameters:
            if parameter.getName() == name:
                return parameter
        return None

class Database:
    def __init__(self,name):
        self.name = name
        self.sections = []
        
    def addSection(self,section):
        self.sections.append(section)
        
    def getSections(self):
        return self.sections
    
    def getSection(self,name):
        for section in self.sections:
            if section.getName() == name:
                return section
        return None
        
class Tab:
    def __init__(self,name):
        self.tabName=name
        self.tabWidget  = QtGui.QWidget()
        self.gridTabWidget = QtGui.QGridLayout()
        self.gridTabWidget.setSpacing(10)
        self.tabWidget.setLayout(self.gridTabWidget)
        self.textBoxes = []
        
    def addTextBox(self,x,y,text,tooltip,name):
        textBox = QtGui.QLineEdit()
        textBox.setText(str(text))
        textBox.setToolTip(tooltip)
        self.gridTabWidget.addWidget(textBox,x,y)
        textBox.setObjectName(name)
        
    def addCheckBox(self,x,y,text,value,tooltip,name):
        checkBox = QtGui.QCheckBox(text)
        checkBox.setChecked(value)
        checkBox.setToolTip(tooltip)
        self.gridTabWidget.addWidget(checkBox,x,y)
        checkBox.setObjectName(name)
        
    def addLabel(self,x,y,text,tooltip):
        label = QtGui.QLabel(text)
        label.setToolTip(tooltip)
        self.gridTabWidget.addWidget(label,x,y)
        
    def getTabWidget(self):
        return self.tabWidget
        
    def getTabName(self):
        return self.tabName
        

class GUI(QtGui.QMainWindow):   
    def __init__(self,main,app,database):
        super(GUI, self).__init__()
        self.app = app
        self.main = main
        self.database = database
        self.widget = QtGui.QWidget()
        self.widget.resize(500,300)
        maingrid = QtGui.QGridLayout(self.widget)
        self.widget.setLayout(maingrid)
        grid_inner = QtGui.QGridLayout(self.widget)
        self.wid_inner = QtGui.QWidget(self.widget)
        self.wid_inner.setLayout(grid_inner)
        maingrid.addWidget(self.wid_inner)
        self.wid_inner.tab = QtGui.QTabWidget(self.wid_inner)
        grid_inner.addWidget(self.wid_inner.tab,0,0,1,2)
        buttonOK = QtGui.QPushButton("OK")
        buttonCancel = QtGui.QPushButton("Cancel")
        buttonCancel.clicked.connect(self.buttonCancelClicked)
        buttonOK.clicked.connect(self.buttonOKclicked)
        grid_inner.addWidget(buttonOK,1,0)
        grid_inner.addWidget(buttonCancel,1,1)
        self.app.aboutToQuit.connect(self.windowCloseEvent)
        
    def addTab(self,tabname,tabWidget):
        self.wid_inner.tab.addTab(tabWidget, tabname)    
        
    def show(self):
        self.widget.show()
        self.app.exec_()
        
    def buttonOKclicked(self):
        self.saveCFG()
        
    def buttonCancelClicked(self):
        self.main.exitApplication()
        
    def windowCloseEvent(self):
        flags = QtGui.QMessageBox.StandardButton.Yes | QtGui.QMessageBox.StandardButton.No
        response = QtGui.QMessageBox.question(self, "Save?", "Save file?", flags)
        if response == QtGui.QMessageBox.Yes:
            self.saveCFG()
        
    def connectEditingFinished(self):
        textBoxes = self.wid_inner.findChildren(QtGui.QLineEdit)
        checkBoxes = self.wid_inner.findChildren(QtGui.QCheckBox)
        for textBox in textBoxes:
            textBox.editingFinished.connect(self.textBoxEditingFinished)
        for checkBox in checkBoxes:
            checkBox.stateChanged.connect(self.checkBoxStateChanged)
            
    def checkBoxStateChanged(self):
        try:
            currentSection = self.wid_inner.tab.tabText(self.wid_inner.tab.currentIndex())
            currentParameterName = self.sender().objectName()
            currentParameter = self.database.getSection(currentSection).getParameter(currentParameterName)
        except ValueError:
            self.sender().undo()
        except AttributeError:
            self.sender().undo()
                
        for param in self.database.getSection(currentSection).getParameters():
            if type(param.getValue()) is str:
                exec(param.getName() + " = '" + str(param.getValue()) + "'")
            elif type(param.getValue()) is float or type(param.getValue()) is bool:
                exec(param.getName() + " = " + str(param.getValue()))
        
        if eval(currentParameter.getCondition()): 
            currentParameter.setValue(self.sender().isChecked())
        else:
            QtGui.QMessageBox.information(self, "Error", "Condition not satisfied")
            self.sender().undo()
        
    def textBoxEditingFinished(self):
        if self.sender().isModified():
            try:
                currentSection = self.wid_inner.tab.tabText(self.wid_inner.tab.currentIndex())
                currentParameterName = self.sender().objectName()
                currentParameter = self.database.getSection(currentSection).getParameter(currentParameterName)
            except ValueError:
                self.sender().undo()
            except AttributeError:
                self.sender().undo()
                
            for param in self.database.getSection(currentSection).getParameters():
                if type(param.getValue()) is str:
                    exec(param.getName() + " = '" + str(param.getValue()) + "'")
                elif type(param.getValue()) is float or type(param.getValue()) is bool:
                    exec(param.getName() + " = " + str(param.getValue()))
            
            if eval(currentParameter.getCondition()): 
                currentParameter.setValue((type(currentParameter.getValue()))(self.sender().text()))
            else:
                QtGui.QMessageBox.information(self, "Error", "Condition not satisfied")
                self.sender().undo()
        self.sender().setModified(False)
        
    def saveCFG(self):
        try:
            fname, _ = QtGui.QFileDialog.getSaveFileName(self, 'Save Config', filter="Config file (*.cfg)")
            if fname.endswith(".cfg"):
                self.main.saveCFG(self.database,fname)
            else:
                fname = fname + ".cfg"
                self.main.saveCFG(self.database,fname)
        except TypeError:
            return

class main:     
    def run(self,argv): 
        IOParameter.init()
        if len(argv) > 1:    
            filename = argv[1]
            IOParameter.read(filename)
        database = self.readDatabase()
        self.drawGUI(database)
        
    def drawGUI(self,database):
        app = QtGui.QApplication(sys.argv)
        gui = GUI(self,app,database)
        for section in database.getSections():
            tab = Tab(section.getName())
            row = 0
            for param in section.getParameters():
                if isinstance(param.getValue(),bool):
                    tab.addCheckBox(row,0,param.getName(),param.getValue(),param.getComment(),param.getName())
                else:
                    tab.addLabel(row,0,param.getName(),param.getComment())
                    tab.addTextBox(row,1,param.getValue(),param.getComment(),param.getName())
                row = row + 1
            gui.addTab(tab.getTabName(),tab.getTabWidget())
        gui.connectEditingFinished()
        gui.show()
        
    def readDatabase(self):
        PARAMETER = IOParameter.PARAMETER
        CONDITION = IOParameter.CONDITION
        COMMENT = IOParameter.COMMENT
        database = Database("parameters.db")       
        for sectionName in PARAMETER.sections():
            section = Section(sectionName)
            for item in PARAMETER.items(sectionName):
                paramName = item[0].upper()
                typ = IOParameter.checktypeparameter(sectionName,item[0])
                if typ == 'string':
                    paramValue = str(item[1])
                elif typ == 'float':
                    paramValue = float(item[1])                    
                elif typ == 'bool':
                    paramValue = str(item[1]) in ["True","true","TRUE"]
                else:
                    paramValue = None   
                paramComment = COMMENT.get(sectionName,item[0])
                paramCondition = CONDITION.get(sectionName,item[0])
                #print(paramName + " \t \t " + str(paramValue) + " \t "  +  type(paramValue).__name__  +  " \t " + paramComment + " \t " + paramCondition)
                param = Parameter(paramName,paramValue,paramComment,paramCondition)
                section.addParameter(param)
            database.addSection(section)
        return database
        
    def saveCFG(self,database,filename):
        config = configparser.RawConfigParser()
        config.optionxform=str
        for section in database.getSections():
            config.add_section(section.getName())
            for param in section.getParameters():
                config.set(section.getName(), param.getName().upper(),param.getValue())
        with open(filename, 'w', encoding='utf8') as configfile:
            config.write(configfile)
    
    def exitApplication(self):
        QtCore.QCoreApplication.instance().quit()
        
if __name__ == '__main__':
    main().run(sys.argv)
