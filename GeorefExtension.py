# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeorefExtension
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
#import debugpy
#debugpy.configure(python='C:/OSGeo4W/apps/Python312/python.exe')
#debugpy.listen(('0.0.0.0',5678))

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, QObject, QAbstractItemModel
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMainWindow, QGraphicsView, QDialogButtonBox, QWidget, QToolBar, QMessageBox, QDialog
from qgis.PyQt.QtXml import *

from qgis.gui import QgsColorDialog, QgsMapCanvas, QgsMessageBar
from qgis.core import Qgis, QgsCoordinateReferenceSystem, QgsProject, QgsReadWriteContext, QgsMapLayerType, QgsRasterLayer, QgsSettings 


# Import the code for the dialog
from .GeorefExtension_dialog import GeorefExtensionDialog
import os, gc, tempfile, re, pathlib

from osgeo import osr,gdal,ogr
gdal.SetConfigOption('GDAL_CACHEMAX','1024')
gdal.SetConfigOption('GDALWARP_DENSIFY_CUTLINE','NO')
gdal.SetConfigOption('GDAL_XML_VALIDATION','NO')
gdal.SetConfigOption('VRT_VIRTUAL_OVERVIEWS','NO')


if os.getenv('GDAL_PDF_DPI'):
    gdal.SetConfigOption('GDAL_PDF_DPI',os.getenv('GDAL_PDF_DPI'))
else:
    os.environ['GDAL_PDF_DPI'] = '250'
    gdal.SetConfigOption('GDAL_PDF_DPI','250')



class GeorefExtension:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        self.toolBarFile = None
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'GeorefExtension_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        action = self.iface.mainWindow().findChild(QAction, 'mActionShowGeoreferencer')
        if action:
            action.triggered.connect(self.addButtons)
            self.dlg = GeorefExtensionDialog()
            self.dlg.editDataSource.textEdited.connect(self.disableOkButton)
            self.dlg.editFileName.fileChanged.connect(self.chkDestinationFileName)
            self.dlg.btnRefresh.clicked.connect(self.updateDataSource)
            self.settings = QSettings()
        else:
            self.iface.messageBar().pushMessage(text="Module 'Georeferencer Extension': The module cannot be installed - Please activate module 'Georeferencer GDAL' first!", level=Qgis.Warning, duration=20)

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None


    def addButtons(self):
        self.gui = self.iface.mainWindow().findChild(QMainWindow,'QgsGeorefPluginGuiBase')
        if self.gui:
            #self.toolBarFile = self.gui.findChild(QObject,'toolBarFile')
            #if self.toolBarFile:
                #self.toolBarFile.addSeparator()
                self.extToolBar = QToolBar("Georef-Extension")
                self.extToolBar.setMovable(True)
                self.gui.addToolBar(self.extToolBar)
                icon = QIcon(self.plugin_dir+"/icons/color.svg")
                self.setBgColorAction = QAction(icon,"Set Backgound Color",self.extToolBar)
                self.setBgColorAction.triggered.connect(self.setGeorefBackgroundColor)
                self.extToolBar.addAction(self.setBgColorAction)
                icon = QIcon(self.plugin_dir+"/icons/delete.svg")
                self.delAllGCPsAction = QAction(icon,"Delete all GCPs",self.extToolBar)
                self.delAllGCPsAction.triggered.connect(self.deleteAllGCPs)
                self.extToolBar.addAction(self.delAllGCPsAction)
                icon = QIcon(self.plugin_dir+"/icons/go.svg")
                self.tranformAndSaveAction = QAction(icon,"Create Virtual Raster",self.extToolBar)
                self.tranformAndSaveAction.triggered.connect(self.transformAndSave)
                self.extToolBar.addAction(self.tranformAndSaveAction)

                canvas = self.iface.mainWindow().findChild(QgsMapCanvas,'georefCanvas')
                canvas.layersChanged.connect(self.getRasterParameters)

                action = self.iface.mainWindow().findChild(QAction, 'mActionShowGeoreferencer')
                action.triggered.disconnect(self.addButtons)

    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        return QCoreApplication.translate('GeorefExtension', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToRasterMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        pass


    def unload(self):
        # remove toolbar actions
        try:
            self.gui.removeToolBar(self.extToolBar)
        except:
            pass

    def atof(self,txt):
        return float('%s.%s' % (re.sub(r'[^\d-]','',re.sub(r'(.+)[,.]\d+$',r'\1',txt)),re.search('(\d+)$',txt)[0]))

    def disableOkButton(self):
        self.dlg.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

    def updateDataSource(self):
        canvas = self.iface.mainWindow().findChild(QgsMapCanvas,'georefCanvas')
        if len(canvas.layers()) == 0:
            return

        layer = canvas.layers()[0]
        fname = self.getSrcFileWithOpenOptions(self.dlg.editDataSource.text())[0]
        if not self.checkSourceFile(fname):
            return
        self.setDataSource(layer,'gdal',self.dlg.editDataSource.text(),None,canvas)
        res = self.getRasterParameters(True)
        if res:
            self.updateDialog(layer)

    def checkSourceFile(self,file):
        if file:
            fn = re.findall(r'^(PDF:\d+:)*([^|]+)',file,re.IGNORECASE)[0][1]
            if not pathlib.Path(fn).is_file():
                self.dlg.lblMessage.setText("Source File does not exist")
                return ''
            else:
                return fn
        else:
            self.dlg.editDataSource.setText(self.canvas.layers()[0].source())
            self.dlg.lblMessage.setText("")
            self.dlg.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
            return ''
    
    def getSrcFileWithOpenOptions(self,src):
        resDict = dict((k.upper(),v) for k,v in re.findall(r'[|]option[:]([^=]+)=([^|]+)',src,re.M|re.IGNORECASE))
        if len(resDict) > 0:
            fn = re.findall(r'^([^|]+)[|]option[:]',src,re.IGNORECASE)[0] 
            return [fn,resDict]
        else:
            return [src]

    def getRasterParameters(self,refresh=False):
        canvas = self.iface.mainWindow().findChild(QgsMapCanvas,'georefCanvas')
        if len(canvas.layers()) == 0:
            return False

        layer = canvas.layers()[0]

        try:
            layerSrsId = int(re.search(r'\d+',layer.crs().authid())[0])
            self.dlg.projSelectWkt.setCrs(QgsCoordinateReferenceSystem.fromEpsgId(layerSrsId))
        except:
            pass

        self.dlg.editDataSource.setText(layer.source())
        fileName = self.getSrcFileWithOpenOptions(layer.source())[0]
        fn = self.checkSourceFile(fileName)
        if not fn:
            return False
    
        filePath, file_extension = os.path.splitext(fn)
        destFile = filePath + '.vrt'
        destPath = os.path.dirname(destFile)

        # if destPath is not writeable, set destFile to write into temp directory
        if (not os.access(destPath,os.W_OK)):
            destPath = tempfile.gettempdir()
            destFile = destPath + '\\' + os.path.basename(destFile)


        self.dlg.setFileName(destFile)

        try:
            src_ds = gdal.Open(fileName)
        except:
            self.dlg.lblMessage.setText("Wrong Datasource definition.")
            return False

        if src_ds:
            try:
                prj = src_ds.GetProjection()
                srs = osr.SpatialReference(wkt=prj)
                srs.AutoIdentifyEPSG()
                #epsg = srs.GetAttrValue("AUTHORITY", 1)
                epsg = srs.GetAuthorityCode(None)
                self.dlg.lblMessage.setText("Input File is already projected (EPSG:%s)" % epsg)
            except:
                self.dlg.lblMessage.setText("")
                pass

            if not refresh:
                self.dlg.editWkt.setPlainText("")
                self.dlg.chkLoad.setChecked(True)

            if src_ds.RasterCount == 1:
                band = src_ds.GetRasterBand(1)
                colorTable = band.GetColorTable()
                if colorTable:
                    for i in range(0, colorTable.GetCount()):
                        entry = colorTable.GetColorEntry(i)
                        if entry == (255, 255, 255, 255):
                            self.dlg.editNodata.setText(str(i))
                            break
        return True

    def setGeorefBackgroundColor(self):
        canvas = self.iface.mainWindow().findChild(QGraphicsView,'georefCanvas')
        if canvas:
            color = QgsColorDialog.getColor(canvas.canvasColor(),canvas,'Select Georeferencer Background Color')
            if color.isValid():
                canvas.setCanvasColor(color)
                canvas.refresh()

    def deleteAllGCPs(self):
        gui = self.iface.mainWindow().findChild(QMainWindow,'QgsGeorefPluginGuiBase')
        canvas = self.iface.mainWindow().findChild(QGraphicsView,'georefCanvas')
        dockWidget = [o for o in canvas.parent().parent().children() if o.objectName() == 'dockWidgetGCPpoints'][0]
        model = [o for o in dockWidget.children() if type(o).__name__ == 'QTableView'][0].model()
        for _ in range(model.rowCount()):
            gui.deleteDataPoint(0)

    def setDataSource(self, layer, newProvider, newDatasource, extent=None, canvas=None):
        '''
        Method to write the new datasource to a raster Layer
        (C) by Enrico Ferreguti (changeDataSource plugin)
        '''
        XMLDocument = QDomDocument("style")
        XMLMapLayers = XMLDocument.createElement("maplayers")
        XMLMapLayer = XMLDocument.createElement("maplayer")
        context = QgsReadWriteContext()
        layer.writeLayerXml(XMLMapLayer,XMLDocument, context)
        # apply layer definition
        XMLMapLayer.firstChildElement("datasource").firstChild().setNodeValue(newDatasource)
        XMLMapLayer.firstChildElement("provider").firstChild().setNodeValue(newProvider)
        if extent: #if a new extent (for raster) is provided it is applied to the layer
            XMLMapLayerExtent = XMLMapLayer.firstChildElement("extent")
            XMLMapLayerExtent.firstChildElement("xmin").firstChild().setNodeValue(str(extent.xMinimum()))
            XMLMapLayerExtent.firstChildElement("xmax").firstChild().setNodeValue(str(extent.xMaximum()))
            XMLMapLayerExtent.firstChildElement("ymin").firstChild().setNodeValue(str(extent.yMinimum()))
            XMLMapLayerExtent.firstChildElement("ymax").firstChild().setNodeValue(str(extent.yMaximum()))

        XMLMapLayers.appendChild(XMLMapLayer)
        XMLDocument.appendChild(XMLMapLayers)
        layer.readLayerXml(XMLMapLayer, context)
        layer.reload()

        if not canvas:
            #self.iface.actionDraw().trigger()
            self.iface.mapCanvas().refresh()
            self.iface.layerTreeView().refreshLayerSymbology(layer.id())
        else:
            extent = layer.extent()
            canvas.setExtent(extent)
            canvas.refreshAllLayers()
            #canvas.refresh()

    def refreshLayer(self, destFile, hasAlpha):
        canvas = self.iface.mapCanvas()
        for layer in (lay for i,lay in QgsProject.instance().mapLayers().items() if lay.type() == QgsMapLayerType.RasterLayer):
            if pathlib.Path(layer.publicSource()).resolve() == pathlib.Path(destFile).resolve():
                
                # create temporary layer to force QGIS adding statistics to VRT file, else we will eventually loose a possible cutline
                tempLayer =  QgsRasterLayer(destFile,"temp", 'gdal')
                tempLayer.reload()
                
                # refresh datasource
                layerId = layer.id()
                self.setDataSource(layer,'gdal',tempLayer.source(),tempLayer.extent())

                rend = layer.renderer()
                if hasAlpha:
                    rend.setAlphaBand(layer.bandCount())
                else:
                    rend.setAlphaBand(-1) # alpha None = -1
                layer.triggerRepaint()
                # remove tempLayer
                QgsProject.instance().removeMapLayers([tempLayer.id()])

    def chkDestinationFileName(self):
        if not(hasattr(self,'canvas')):
            return
        
        destFile = self.dlg.getFileName().lower().replace('\\','/')
        if not(os.access(os.path.dirname(destFile), os.W_OK)):
            self.dlg.lblMessage.setText('Invalid Output file!')
            self.dlg.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
            return


        layer = self.canvas.layers()[0]
        srcFile = self.checkSourceFile(self.getSrcFileWithOpenOptions(layer.source())[0].lower().replace('\\','/'))
        if srcFile == destFile:
            self.dlg.lblMessage.setText('Output file must not match Source file!')
            self.dlg.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        else:
            self.dlg.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)

    def updateDialog(self,layer):
        src = self.getSrcFileWithOpenOptions(layer.source())
        srcFile = self.checkSourceFile(src[0])
        openParams = None
        if len(src) > 1:
            openParams = src[1]
        
        
        sourceSRS = layer.crs().authid()
        srsID = None
        try:
            srsID = int(re.search(r'\d+',sourceSRS)[0])
            self.dlg.projSourceSelect.setCrs(QgsCoordinateReferenceSystem.fromEpsgId(srsID))
        except:
            pass
            
        if self.settings.value("Plugin-GeoReferencer/targetsrs"):
            tgtID = int(self.settings.value("Plugin-GeoReferencer/targetsrs"))
            self.dlg.projSelect.setCrs(QgsCoordinateReferenceSystem.fromEpsgId(tgtID))

        self.dlg.editWkt.setFocus()
        self.chkDestinationFileName()
        
        return src[0],openParams

    def transformAndSave(self):
        #debugpy.log_to('C:/OSGeo4W/logs')
        #debugpy.wait_for_client()  # blocks execution until client is attached
        #debugpy.breakpoint()
        self.dlg.lblMessage.setText('')
        self.canvas = self.iface.mainWindow().findChild(QGraphicsView,'georefCanvas')
        if not(hasattr(self,'canvas')) or len(self.canvas.layers()) == 0:
            return
        
        layer = self.canvas.layers()[0]
        self.dlg.editDataSource.setText(layer.source())

        self.updateDialog(layer)

        if self.dlg.exec_():
            srcFile,openParams = self.updateDialog(layer)

            if not srcFile:
                return

            targetSRS = self.dlg.projSelect.crs().authid()
            tgtID = int(re.search(r'\d+',targetSRS)[0])
            #if targetSRS[0:4] == 'EPSG':
            #    self.settings.setValue("/Plugin-GeoReferencer/targetsrs", tgtID)

            cutlineWkt = self.dlg.getWkt()
            if '\n' in cutlineWkt:
                i = cutlineWkt.index('\n')+1
                cutlineWkt = cutlineWkt[i:]

            if cutlineWkt != '':
                # convert cutline from cutlineSRS to targetSRS and save WKT as CUTLINE Metadata node
                cutlineWktCrs = self.dlg.projSelectWkt.crs().authid()
                cutlineWktCrsID = int(re.search(r'\d+',cutlineWktCrs)[0])
                cutlineSRS = osr.SpatialReference()
                cutlineSRS.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
                cutlineSRS.ImportFromEPSG(cutlineWktCrsID)
                cutlineTargetSRS = osr.SpatialReference()
                cutlineTargetSRS.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
                cutlineTargetSRS.ImportFromEPSG(tgtID)
                transform = osr.CoordinateTransformation(cutlineSRS, cutlineTargetSRS)
                try:
                    poly = ogr.CreateGeometryFromWkt(cutlineWkt) # new Poly is in 3D
                except:
                    msg = 'Invalid Cutline WKT string!'
                    self.transformAndSave(msg)
                    return
                #poly.FlattenTo2D() # flatten to 2D
                poly.Transform(transform)
                newCutlineWkt = poly.ExportToWkt()
                
            destFile = self.dlg.getFileName()
            openOptions = None

            cont = True

            if openParams:
                openOptions = ['%s=%s' % (key,value) for (key,value) in openParams.items()]
                  
                try:
                    src_ds = gdal.OpenEx(srcFile, gdal.OF_RASTER | gdal.OF_UPDATE, open_options=openOptions)
                except:
                    cont = False
            else:
                try:
                    src_ds = gdal.Open(srcFile,gdal.GA_ReadOnly)
                except:
                    cont = False

            if not cont:
                QMessageBox.critical(None,"Georeferencer Extension",'Error in Datasource definition.')
                return

            new_options = '-co NUM_THREADS=ALL_CPUS -of VRT -t_srs '+targetSRS+' '
            dst_ds = None
            if destFile:
                noData = self.dlg.getNodata()
                if noData != '':
                    new_options += '-dstnodata '+noData+' '

                if self.dlg.chkAlpha.isChecked():
                    new_options += '-dstalpha '

                widget = self.iface.mainWindow().findChild(QWidget,'dockWidgetGCPpoints')
                model = widget.findChild(QAbstractItemModel)
                gcpList = []

                for i in range(model.rowCount()):
                    gcp = gdal.GCP(self.atof(model.index(i,4).data()),self.atof(model.index(i,5).data()),0,self.atof(model.index(i,2).data()),-(self.atof(model.index(i,3).data())))
                    gcpList.append(gcp)

                gdal.Translate(destName='/vsimem/temp', srcDS=src_ds,format = 'VRT', outputSRS = targetSRS, GCPs = gcpList)
                if openOptions:
                   src_ds_temp = gdal.OpenEx('/vsimem/temp', open_options=openOptions)
                else:
                    src_ds_temp = gdal.OpenEx('/vsimem/temp')

                tempDs = None
                if cutlineWkt != '':
                    # add CUTLINE to src_ds_temp
                    metadata = src_ds_temp.GetMetadata()
                    metadata['CUTLINE'] = newCutlineWkt
                    src_ds_temp.SetMetadata(metadata)
                    
                    new_options += '-co NUM_THREADS=ALL_CPUS -multi -wo NUM_THREADS=ALL_CPUS -wm 1024 -cutline /vsimem/temp.db -crop_to_cutline '
                    polygon = ogr.CreateGeometryFromWkt(cutlineWkt)

                    #create an output datasource in memory
                    outdriver=ogr.GetDriverByName('SQLite')
                    tempDs=outdriver.CreateDataSource('/vsimem/temp.db')


                    tempLayer=tempDs.CreateLayer('temp',srs = cutlineSRS, geom_type=ogr.wkbPolygon)
    
                    # Add an ID field
                    idField = ogr.FieldDefn("id", ogr.OFTInteger)
                    tempLayer.CreateField(idField)

                    # Create the feature and set values
                    featureDefn = tempLayer.GetLayerDefn()
                    feature = ogr.Feature(featureDefn)
                    feature.SetGeometry(polygon)
                    feature.SetField("id", 1)
                    tempLayer.CreateFeature(feature)

                warp_opts = gdal.WarpOptions(options=new_options)
                
                dst_ds = gdal.Warp(destNameOrDestDS=destFile,srcDSOrSrcDSTab=src_ds_temp, options=warp_opts)
                if dst_ds:
                    with open(destFile, 'r+') as f:
                        content = f.read()
                        f.seek(0)
                        f.truncate()
                        f.write(content.replace('relativeToVRT="0">/vsimem/temp','relativeToVRT="0">'+srcFile))

            # load image into canvas
            if not destFile:
                destFile = srcFile

            if self.dlg.chkLoad.isChecked():
                baseName = os.path.basename(destFile)
                rasterLayer = self.iface.addRasterLayer(destFile,baseName)
                extent = rasterLayer.extent()
                # call layer.reload() to force QGIS adding statistics to VRT file
                rasterLayer.reload()
                self.iface.mapCanvas().setExtent(extent)
            else:
                # refresh all dependent raster layers
                self.refreshLayer(destFile,self.dlg.chkAlpha.isChecked())
            if src_ds:
                del src_ds

        # Release memory associated to the in-memory file 
        try:
            gdal.Unlink('/vsimem/temp')
        except:
            pass

        gc.collect()

