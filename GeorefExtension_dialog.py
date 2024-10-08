# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeorefExtensionDialog
                                 A QGIS plugin
 Extension to the Raster Georeferencer Plugin
 
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2020-08-24
        git sha              : $Format:%H$
        copyright            : (C) 2020 by Christoph Candido
        email                : christoph.candido@gmx.at
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from qgis.PyQt.QtCore import QRegExp
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from qgis.gui import QgsProjectionSelectionWidget,QgsFileWidget

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
#FORM_CLASS, _ = uic.loadUiType(os.path.join(
#    os.path.dirname(__file__), 'GeorefExtension_dialog_base.ui'))

class GeorefExtensionDialog(QDialog):
    def __init__(self, parent=None):
        super(GeorefExtensionDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        #self.setupUi(self)
        self.setWindowTitle("Create Virtual Raster")
        self.resize(500,300)
        layout = QVBoxLayout(self)
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.editFileName = QgsFileWidget(self)
        self.lblFileName = QLabel('&Output File:')
        self.lblFileName.setBuddy(self.editFileName)
        self.editNodata = QLineEdit()
        regex = QRegExp(r'[-]{0,1}\d+')
        #self.editNodata.setPlaceholderText('-9999')
        self.editNodata.setValidator(QRegExpValidator(regex))
        self.lblNodata = QLabel('&NoData Value:')
        self.lblNodata.setBuddy(self.editNodata)
        self.editWkt = QPlainTextEdit()
        self.chkAlpha = QCheckBox('Create &Alpha Channel')
        self.chkLoad = QCheckBox('&Load in QGIS when done')
        self.projSelect = QgsProjectionSelectionWidget()
        self.lblTargetSRS = QLabel('&Target SRS:')
        self.lblTargetSRS.setBuddy(self.projSelect)
        self.projSelectWkt = QgsProjectionSelectionWidget()
        self.lblWktSRS = QLabel('&Cutline SRS:')
        self.lblWktSRS.setBuddy(self.projSelectWkt)
        self.lblEditWkt = QLabel('Enter Cutline WKT:')
        self.lblEditWkt.setBuddy(self.editWkt)
        self.lblMessage = QLabel('')
        self.lblMessage.setStyleSheet("color:red")
        layout.addWidget(self.lblFileName)
        layout.addWidget(self.editFileName)
        layout.addWidget(self.lblNodata)
        layout.addWidget(self.editNodata)
        layout.addWidget(self.chkAlpha)
        layout.addWidget(self.chkLoad)
        layout.addWidget(self.lblTargetSRS)
        layout.addWidget(self.projSelect)
        layout.addWidget(self.lblWktSRS)
        layout.addWidget(self.projSelectWkt)
        layout.addWidget(self.lblEditWkt)
        layout.addWidget(self.editWkt)
        layout.addWidget(self.lblMessage)
        layout.addWidget(self.buttonBox)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def getWkt(self):
        return self.editWkt.toPlainText()
    
    def getNodata(self):
        return self.editNodata.text()

    def getFileName(self):
        return self.editFileName.filePath()
        
    def setFileName(self,filePath):
        root = os.path.dirname(filePath)
        self.editFileName.setDefaultRoot(root)
        self.editFileName.setFilePath(filePath)
