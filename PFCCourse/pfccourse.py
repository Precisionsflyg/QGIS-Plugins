# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PFCCourse
                                 A QGIS plugin
 Builds a course for Precision Flying Competitions
                              -------------------
        begin                : 2016-04-17
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Joakim Mårtensson
        email                : calder2@telia.com
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QVariant
from PyQt4.QtGui import QAction, QIcon, QFileDialog
from qgis.core import *
from qgis.gui import QgsMessageBar
import math

# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from pfccourse_dialog import PFCCourseDialog
from pfccourse_dialog_settings import PFCCourseDialogSettings
import os.path


class PFCCourse:
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
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'PFCCourse_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = PFCCourseDialog()
        self.sdlg = PFCCourseDialogSettings()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&PFC Course Builder')
        # TODO: We are going to let the user set this up in a future iteration
        
        #No toolbar for now...
        #self.toolbar = self.iface.addToolBar(u'PFCCourse')
        #self.toolbar.setObjectName(u'PFCCourse')
        
        # Global CourseDirectory
        # See if we already have a CourseDirectory setting
        sp = QgsProject.instance()
        spcd = sp.readEntry("PFCCourse", "CourseDirectory", "C:\\")[0]
        self.globalCourseDirectory = spcd

        # Global Layer Pointer - Start with selected
        spcp = sp.readEntry("PFCCourse", "CoursePointlayer", "")[0]
        #print "CoursePointlayer from Settings: ", spcp
        #if spcp == "":
        #    self.selectedLayerGlobal = self.iface.legendInterface().currentLayer()#Choose current instead
        #else:
        #    self.selectedLayerGlobal = QgsMapLayerRegistry.instance().mapLayersByName(spcp)[0]

        self.sdlg.lineEditDirectory.clear()
        self.sdlg.pushButtonDirectory.clicked.connect(self.select_courses_directory)


    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('PFCCourse', message)


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
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def haversine(self, lon1, lat1, lon2, lat2):
        """
        Calculate the great circle distance between two points 
        on the earth (specified in decimal degrees)
        """
        # convert decimal degrees to radians 
        lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
        # haversine formula 
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a)) 
        km = 6367 * c
        nm = km / 1.852
        return nm
    
    def haversinePoints(self, startPoint, endPoint):
        """
        Calculate the great circle distance between two points 
        on the earth (specified in decimal degrees)
        """
        lon1 = startPoint.x()
        lat1 = startPoint.y()
        lon2 = endPoint.x()
        lat2 = endPoint.y()
        # Convert decimal degrees to radians 
        lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
        # Haversine formula 
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a)) 
        km = 6367 * c
        nm = km / 1.852
        return nm
    
    def calculateBearing(self, startPoint, endPoint):
        crs = QgsCoordinateReferenceSystem(4326)    # WGS 84
        d = QgsDistanceArea()
        #print d.sourceCrs
        d.setSourceCrs(crs)#WGS84
        d.setEllipsoid(crs.ellipsoidAcronym())
        d.setEllipsoidalMode(crs.geographicFlag())

        calcOutboundSigned = d.bearing(startPoint, endPoint) * 180/math.pi #Convert to Degrees
        calcOutbound = 0
        if calcOutboundSigned < 0:
            calcOutbound = 360 + calcOutboundSigned
        else:
            calcOutbound = calcOutboundSigned
        return calcOutbound
        
    def doesLineLayerExist(self, pointLayer):
        # Check if we already have a linelayer based on the selected pointlayer
        # Pointlayer should be named: [COURSENAME]_[NUMBER]_[DIRECTION (CW-clockwise or CCW)] e.g. Kristianstad_01_CW
        # Corresponding linelayer will get its name by appending: "_Lines"
        
        doesNotExist = 0
        doesExistNotLoaded = 1
        doesExistLoadedInLegend = 2
        unknownError = 99
        
        lineLayerNameToCheck = pointLayer.name() + "_Lines"
        
        layers = self.iface.legendInterface().layers()
        layer_list = []
        for layer in layers:
            if layer.type() == 0:# 0=VectorLayer
                if layer.geometryType() == 1: # 0=Pointlayer, 1=Linelayer, 2=Polygonlayer
                    layer_list.append(layer.name())

        if lineLayerNameToCheck in layer_list:
            # Already exists in the layerlegend!
            #print "Found: ", lineLayerNameToCheck
            return doesExistLoadedInLegend
            
        # Try to load layer if it doesn't exist in the legend
        pathname = lineLayerNameToCheck + ".shp"
        path = os.path.join(self.globalCourseDirectory, pathname)
        path = os.path.abspath(path)
        #print "FileWriter Path: ", path
        
        #path = self.globalCourseDirectory + "\\" + lineLayerNameToCheck + ".shp"
        #print path
        nameYouLike = lineLayerNameToCheck
        vlayer = QgsVectorLayer(path, nameYouLike, "ogr")
        if not vlayer.isValid():
            #print "Layer failed to load!"
            vlayer = None
            return doesNotExist
        else:
            #QgsMapLayerRegistry.instance().addMapLayer(vlayer)
            vlayer = None
            return doesExistNotLoaded

        return unknownError
        
    def doesReverseCourseLayerExist(self, pointLayer):
        # Check if we already have a reverse pointlayer based on the selected pointlayer
        # Pointlayer should be named: [COURSENAME]_[NUMBER]_[DIRECTION (CW-clockwise or CCW)] e.g. Kristianstad_01_CW
        # Reversed pointlayer will get its name by alternating CW or CCW...
        
        doesNotExist = 0
        doesExistNotLoaded = 1
        doesExistLoadedInLegend = 2
        wrongName = 3
        unknownError = 99
        
        pointLayerNameToCheck = pointLayer.name()
        intCheck = pointLayerNameToCheck.find(' CCW') # -1 if not found, otherwise index
        #print 'Found CCW: ', intCheck
        if intCheck == -1: # Not found
            intCheck = pointLayerNameToCheck.find(' CW') # -1 if not found, otherwise index
            #print 'Found CW: ', intCheck
            if intCheck == -1: # Still not found
                return wrongName
            else: # Found ClockWise course, let's search for a Counter ClockWise course
                #print 'Name before: ', pointLayerNameToCheck
                pointLayerNameToCheck = pointLayerNameToCheck.replace('CW','CCW')
                #print 'Name after: ', pointLayerNameToCheck

        else: # Found Counter ClockWise course, let's search for a ClockWise course
            #print 'Name of CCW before: ', pointLayerNameToCheck
            pointLayerNameToCheck = pointLayerNameToCheck.replace('CCW','CW')
        
        layers = self.iface.legendInterface().layers()
        layer_list = []
        for layer in layers:
            if layer.type() == 0:# 0=VectorLayer
                if layer.geometryType() == 0: # 0=Pointlayer, 1=Linelayer, 2=Polygonlayer
                    layer_list.append(layer.name())

        if pointLayerNameToCheck in layer_list:
            # Already exists in the layerlegend!
            #print "Found: ", pointLayerNameToCheck
            return doesExistLoadedInLegend
            
        # Try to load layer if it doesn't exist in the legend
        pathname = pointLayerNameToCheck + ".shp"
        path = os.path.join(self.globalCourseDirectory, pathname)
        path = os.path.abspath(path)
        #print "FileWriter Path: ", path
        
        #path = self.globalCourseDirectory + "\\" + pointLayerNameToCheck + ".shp"
        #print path
        nameYouLike = pointLayerNameToCheck
        vlayer = QgsVectorLayer(path, nameYouLike, "ogr")
        if not vlayer.isValid():
            #print "Layer failed to load!"
            vlayer = None
            return doesNotExist
        else:
            #QgsMapLayerRegistry.instance().addMapLayer(vlayer)
            vlayer = None
            return doesExistNotLoaded

        return unknownError
        
    def loadLineLayer(self, pointLayer):
        
        lineLayerName = pointLayer.name() + "_Lines"
        pathname = lineLayerName + ".shp"
        path = os.path.join(self.globalCourseDirectory, pathname)
        path = os.path.abspath(path)
        #print "FileWriter Path: ", path
        
        #path = self.globalCourseDirectory + "\\" + lineLayerName + ".shp"
        nameYouLike = lineLayerName
        vlayer = QgsVectorLayer(path, nameYouLike, "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(vlayer)
        
    def loadCourseLayer(self, pointLayer):
        
        pointLayerNameToCheck = pointLayer.name()
        intCheck = pointLayerNameToCheck.find(' CCW') # -1 if not found, otherwise index
        if intCheck == -1: # Not found
            intCheck = pointLayerNameToCheck.find(' CW') # -1 if not found, otherwise index
            if intCheck == -1: # Still not found
                return
            else: # Found ClockWise course, let's search for a Counter ClockWise course
                pointLayerNameToCheck = pointLayerNameToCheck.replace('CW','CCW')
        else: # Found Counter ClockWise course, let's search for a ClockWise course
            pointLayerNameToCheck = pointLayerNameToCheck.replace('CCW','CW')

        courseLayerName = pointLayerNameToCheck
        pathname = courseLayerName + ".shp"
        path = os.path.join(self.globalCourseDirectory, pathname)
        path = os.path.abspath(path)
        #print "FileWriter Path: ", path
        
        #path = self.globalCourseDirectory + "\\" + courseLayerName + ".shp"
        nameYouLike = courseLayerName
        vlayer = QgsVectorLayer(path, nameYouLike, "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(vlayer)
        
    def getOrderedListOfSCForLeg(self,leg):
        #print "Inne..."
        orderedList = []
        iter = self.selectedLayerGlobal.getFeatures()
        for feature in iter:
            # fetch geometry
            geom = feature.geometry()
            if geom.type() == QGis.Point:
                #print feature.attribute('Category')
                if feature.attribute('Category') == 'SC':
                    #print feature.attribute('Leg')
                    typecastLeg = int(feature.attribute('Leg'))
                    if typecastLeg == leg:
                        orderedList.append(feature)
                        #print "Found Secret Checkpoint on leg: ", leg
                    else:
                        pass
                        #print "Wrong leg, skipping SC."
            else:
                #print "Wrong Layer?"
                
        orderedList.sort(key=lambda x: x[2]) # Sort by third column (Number), unsafe?
        
        return orderedList # Only a list of SC

    def getOrderedFeatureListFromLayer(self):
        orderedList = []
        startingPoint = QgsFeature()
        finishPoint = QgsFeature()
            
        iter = self.selectedLayerGlobal.getFeatures()
        for feature in iter:
            # fetch geometry
            geom = feature.geometry()
            if geom.type() == QGis.Point:
                if feature.attribute('Category') == 'SP':
                    startingPoint = feature
                    #print "Found Starting Point"
                elif feature.attribute('Category') == 'FP':
                    finishPoint = feature
                    #print "Found Finish Point"
                elif feature.attribute('Category') == 'TP':
                    orderedList.append(feature)
                    #print "Found TP" + str(feature.attribute('Number'))
                else:
                    pass
                    #print "Other type (maybe SC), skipping"
            else:
                #print "Wrong Layer?"
            
        orderedList.sort(key=lambda x: x[2]) # Sort by Number
        orderedList.insert(0, startingPoint)
        orderedList.append(finishPoint)
        
        return orderedList # Only SP, TP and FP
    
    def writeFugawiFile(self):
        self.updateSettings()
        orderedList = self.getOrderedFeatureListFromLayer()
        
        pathname = self.selectedLayerGlobal.name() + ".txt"
        path = os.path.join(self.globalCourseDirectory, pathname)
        path = os.path.abspath(path)
        #print "Path: ", path

        #path = self.globalCourseDirectory + "\\" + self.selectedLayerGlobal.name() + ".txt"
        output_file = open(path, 'w')
        line = '# Each record includes the following fields\n'
        unicode_line = line.encode('cp1252')
        output_file.write(unicode_line)
        line = '#\n'
        unicode_line = line.encode('cp1252')
        output_file.write(unicode_line)
        line = '#    Waypoint Name\n'
        unicode_line = line.encode('cp1252')
        output_file.write(unicode_line)
        line = '#    Waypoint Comment\n'
        unicode_line = line.encode('cp1252')
        output_file.write(unicode_line)
        line = '#    Latitude in decimal degrees (negative is south)\n'
        unicode_line = line.encode('cp1252')
        output_file.write(unicode_line)
        line = '#    Longitude in decimal degrees (negative is west)\n'
        unicode_line = line.encode('cp1252')
        output_file.write(unicode_line)

        currentOrderedListIndex = 0
        leg = 1
        for feature in orderedList:
            currentFeatureIndex = feature.id()
            #print feature.attribute('Category')
            if feature.attribute('Category') != 'FP':
                # Write SP or TP with coordinates
                pseudoCategory = feature['Category']
                if pseudoCategory == 'TP':
                    pseudoCategory = pseudoCategory + str(feature['Number'])
                point01 = feature.geometry().asPoint()
                line = '%s,%s,%f,%f\n' % (pseudoCategory, feature['Descr'], point01.y(), point01.x())
                unicode_line = line.encode('cp1252')
                output_file.write(unicode_line)
                
                # Get a sorted list of Secret Checkpoints for the current leg
                legFromFeature = int(feature.attribute('Leg'))
                #print "legFromFeature: ", legFromFeature, "leg: ", leg
                if legFromFeature is not NULL:
                    if leg == legFromFeature:
                        #print "Inne..."
                        listSC = self.getOrderedListOfSCForLeg(leg)
                        for sc in listSC:
                            # Write SC
                            #print "Skriver..."
                            point01 = sc.geometry().asPoint()
                            pseudoCategory = sc['Category'] + str(sc['Leg']) + '/' + str(sc['Number'])
                            line = '%s,,%f,%f\n' % (pseudoCategory, point01.y(), point01.x())
                            unicode_line = line.encode('cp1252')
                            output_file.write(unicode_line)
                
            elif feature.attribute('Category') == 'FP':
                # Write SP or TP with coordinates
                pseudoCategory = feature['Category']
                point01 = feature.geometry().asPoint()
                line = '%s,%s,%f,%f\n' % (pseudoCategory, feature['Descr'], point01.y(), point01.x())
                unicode_line = line.encode('cp1252')
                output_file.write(unicode_line)

            currentOrderedListIndex = currentOrderedListIndex +1
            leg = leg +1
            
        output_file.close()

    
    def calcDistBear(self):
        self.updateSettings()
        orderedList = self.getOrderedFeatureListFromLayer()
        
        crs = self.selectedLayerGlobal.crs()
        d = QgsDistanceArea()
        #print d.sourceCrs
        d.setSourceCrs(crs)#WGS84
        d.setEllipsoid(crs.ellipsoidAcronym())
        d.setEllipsoidalMode(crs.geographicFlag())
        
        currentOrderedListIndex = 0
        leg = 1
        for feature in orderedList:
            currentFeatureIndex = feature.id()
            #print feature.attribute('Category')
            if feature.attribute('Category') != 'FP':
                point01 = feature.geometry().asPoint()
                point02 = orderedList[currentOrderedListIndex+1].geometry().asPoint()
                #calcDist = d.measureLine(point01, point02) * 0.0005399568#Convert to NauticalMiles
                calcDist = self.haversine(point01.x(),point01.y(),point02.x(),point02.y())
                calcOutboundSigned = d.bearing(point01, point02) * 180/math.pi#Convert to Degrees
                calcOutbound = 0
                if calcOutboundSigned < 0:
                    calcOutbound = 360 + calcOutboundSigned
                else:
                    calcOutbound = calcOutboundSigned
                #print calcDist, calcOutbound
                # Calculate Inbound TT, if we are not on SP.
                inbTT = 0.0
                if feature.attribute('Category') != 'SP':
                    point00 = orderedList[currentOrderedListIndex-1].geometry().asPoint()
                    inbTT = self.calculateBearing(point00,point01)
                caps = self.selectedLayerGlobal.dataProvider().capabilities()
                if caps & QgsVectorDataProvider.ChangeAttributeValues:
                    attrs = { feature.fieldNameIndex('Leg') : leg, feature.fieldNameIndex('OutbTT') : calcOutbound, feature.fieldNameIndex('InbTT') : inbTT, feature.fieldNameIndex('DistToNext') : calcDist }
                    self.selectedLayerGlobal.dataProvider().changeAttributeValues({ currentFeatureIndex : attrs })
            elif feature.attribute('Category') == 'FP':
                point00 = orderedList[currentOrderedListIndex-1].geometry().asPoint()
                point01 = feature.geometry().asPoint()
                inbTT = 0.0
                inbTT = self.calculateBearing(point00,point01)
                if caps & QgsVectorDataProvider.ChangeAttributeValues:
                    attrs = { feature.fieldNameIndex('InbTT') : inbTT }
                    self.selectedLayerGlobal.dataProvider().changeAttributeValues({ currentFeatureIndex : attrs })
                
            currentOrderedListIndex = currentOrderedListIndex +1
            leg = leg +1

    def createCourseLines(self):
        # Check if the linelayer already exists
        self.updateSettings()
        resultCode = self.doesLineLayerExist(self.selectedLayerGlobal)
        #print resultCode
        if resultCode == 2:
            #print "Layer already exists in legend!"
            self.iface.messageBar().pushMessage("Error", "Courselines for this course already exists! Backup/Delete Shapefile first, before you can create new courselines!", level=QgsMessageBar.CRITICAL, duration=30)
            #We should update the CourseLineLayer instead of creating a new file
            #updateCourseLines(self)
            return
        elif resultCode == 1:
            #print "Layer exists, but is not loaded (yet)!"
            #Load the layer first, then update the CourseLineLayer instead of creating a new file
            self.loadLineLayer(self.selectedLayerGlobal)
            #updateCourseLines(self)
            return
        elif resultCode == 0:
            #print "Layer does not exist!"
            #Lets go ahead and create a new file!
        elif resultCode == 99:
            #print "Uh uh!"
            #Something went wrong, should we fix it?
            return
        resultCode = -1

        #print "Lets go ahead and create a new file"
        # define fields for feature attributes. A QgsFields object is needed
        fields = QgsFields()
        fields.append(QgsField("Category", QVariant.String))
        fields.append(QgsField("Leg", QVariant.Int))
        fields.append(QgsField("Distance", QVariant.Double))
        fields.append(QgsField("Bearing", QVariant.Double))

        # Create an instance of vector file writer, which will create the vector file.
        # Arguments:
        # 1. path to new file (will fail if exists already)
        # 2. encoding of the attributes
        # 3. field map
        # 4. geometry type - from WKBTYPE enum (QGis.WKBLineString)
        # 5. layer's spatial reference (instance of
        #    QgsCoordinateReferenceSystem) - optional
        # 6. driver name for the output file
        coordinateSystem = QgsCoordinateReferenceSystem()
        coordinateSystem.createFromUserInput("EPSG:4326")
        pathname = self.selectedLayerGlobal.name() + "_Lines.shp"
        path = os.path.join(self.globalCourseDirectory, pathname)
        path = os.path.abspath(path)
        #print "FileWriter Path: ", path
        writer = QgsVectorFileWriter(path, "CP1250", fields, QGis.WKBLineString,
                                     coordinateSystem, "ESRI Shapefile")

        if writer.hasError() != QgsVectorFileWriter.NoError:
            #print "Error when creating shapefile: ",  writer.errorMessage()

        # Create FirstPart, CourseLine and LastPart for each leg.
        orderedList = self.getOrderedFeatureListFromLayer()
        currentOrderedListIndex = 0
        for feature in orderedList:
            currentFeatureIndex = feature.id()
            if feature.attribute('Category') != 'FP':
                #print "Leg: ", feature.attribute('Leg')
                circleRadius = 2500/2 # 1.35NM / 10mm on map
                startPoint = feature.geometry().asPoint()
                endPoint = orderedList[currentOrderedListIndex+1].geometry().asPoint()
                
                # Start with FirstPart
                bearing = self.calculateBearing(startPoint,endPoint)
                courseLineStartPoint = self.createPointWithDistanceAndBearingFromPoint(startPoint,
                                                                                       circleRadius,
                                                                                       bearing)
                bearing = self.calculateBearing(startPoint,courseLineStartPoint)
                distance = self.haversinePoints(startPoint,courseLineStartPoint)
                #print "First Part"
                #print "startPoint: ", startPoint, "courseLineStartPoint: ", courseLineStartPoint
                #print "Distance: ", distance, "Bearing: ", bearing
                # Add FirstPart
                fet = QgsFeature()
                fet.setGeometry(QgsGeometry.fromPolyline([startPoint,courseLineStartPoint]))
                fet.setAttributes(["FirstPart", feature.attribute('Leg'), distance, bearing])
                writer.addFeature(fet)

                # Start with LastPart
                reciprocalBearing = self.calculateBearing(endPoint,startPoint)
                #print "reciprocalBearing: ", reciprocalBearing
                courseLineEndPoint = self.createPointWithDistanceAndBearingFromPoint(endPoint,
                                                                                       circleRadius,
                                                                                       reciprocalBearing)
                distance = self.haversinePoints(courseLineEndPoint,endPoint)
                bearing = self.calculateBearing(courseLineEndPoint,endPoint)
                #print "Last Part"
                #print "courseLineEndPoint: ", courseLineEndPoint, "endPoint: ", endPoint
                #print "Distance: ", distance, "Bearing: ", bearing
                # Add LastPart
                fet = QgsFeature()
                fet.setGeometry(QgsGeometry.fromPolyline([courseLineEndPoint,endPoint]))
                fet.setAttributes(["LastPart", feature.attribute('Leg'), distance, bearing])
                writer.addFeature(fet)
                
                # Start with CourseLine
                distance = self.haversinePoints(courseLineStartPoint,courseLineEndPoint)
                bearing = self.calculateBearing(courseLineStartPoint,courseLineEndPoint)
                #print "CourseLine"
                #print "courseLineStartPoint: ", courseLineStartPoint, "courseLineEndPoint: ", courseLineEndPoint
                #print "Distance: ", distance, "Bearing: ", bearing
                # Add CourseLine
                fet = QgsFeature()
                fet.setGeometry(QgsGeometry.fromPolyline([courseLineStartPoint,courseLineEndPoint]))
                fet.setAttributes(["CourseLine", feature.attribute('Leg'), distance, bearing])
                writer.addFeature(fet)
                
            currentOrderedListIndex = currentOrderedListIndex +1

        # delete the writer to flush features to disk
        del writer

        # Check if the linelayer already exists
        resultCode = self.doesLineLayerExist(self.selectedLayerGlobal)
        #print resultCode
        if resultCode == 2:
            #print "Layer already exists in legend!"
        elif resultCode == 1:
            #print "Layer exists, but is not loaded (yet)!"
            self.loadLineLayer(self.selectedLayerGlobal)
        elif resultCode == 0:
            #print "Layer does not exist!"
        elif resultCode == 99:
            #print "Uh uh!"
        resultCode = -1
        
    def createReverseCourse(self):
        # Check if a reverse course already exists
        self.updateSettings()
        resultCode = self.doesReverseCourseLayerExist(self.selectedLayerGlobal)
        #print resultCode
        if resultCode == 2:
            #print "Layer already exists in legend!"
            self.iface.messageBar().pushMessage("Error", "A reverse course for this course already exists! Backup/Delete Shapefile first, before you can create a new reverse course!", level=QgsMessageBar.CRITICAL, duration=30)
            return
        elif resultCode == 1:
            #print "Layer exists, but is not loaded (yet)!"
            #Load the layer first, then update the CourseLineLayer instead of creating a new file
            self.loadCourseLayer(self.selectedLayerGlobal)
            return
        elif resultCode == 3:
            #print "Wrong Layername?"
            return
        elif resultCode == 0:
            #print "Layer does not exist!"
            #Lets go ahead and create a new file!
        elif resultCode == 99:
            #print "Uh uh!"
            #Something went wrong, should we fix it?
            return
        resultCode = -1

        #print "Lets go ahead and create a new file"
        # define fields for feature attributes. A QgsFields object is needed
        fields = QgsFields()
        fields.append(QgsField("Category", QVariant.String))
        fields.append(QgsField("Leg", QVariant.Int))
        fields.append(QgsField("Number", QVariant.Int))
        fields.append(QgsField("Descr", QVariant.String))
        fields.append(QgsField("LblLat", QVariant.Double))
        fields.append(QgsField("LblLong", QVariant.Double))
        fields.append(QgsField("LblRot", QVariant.Double))
        fields.append(QgsField("OutbTT", QVariant.Double))
        fields.append(QgsField("DistToNext", QVariant.Double))

        # Create an instance of vector file writer, which will create the vector file.
        # Arguments:
        # 1. path to new file (will fail if exists already)
        # 2. encoding of the attributes
        # 3. field map
        # 4. geometry type - from WKBTYPE enum (QGis.WKBLineString)
        # 5. layer's spatial reference (instance of
        #    QgsCoordinateReferenceSystem) - optional
        # 6. driver name for the output file
        pointLayerNameToCheck = self.selectedLayerGlobal.name()
        intCheck = pointLayerNameToCheck.find(' CCW') # -1 if not found, otherwise index
        if intCheck == -1: # Not found
            intCheck = pointLayerNameToCheck.find(' CW') # -1 if not found, otherwise index
            if intCheck == -1: # Still not found
                return
            else: # Found ClockWise course, let's search for a Counter ClockWise course
                pointLayerNameToCheck = pointLayerNameToCheck.replace('CW','CCW')
        else: # Found Counter ClockWise course, let's search for a ClockWise course
            pointLayerNameToCheck = pointLayerNameToCheck.replace('CCW','CW')

        coordinateSystem = QgsCoordinateReferenceSystem()
        coordinateSystem.createFromUserInput("EPSG:4326")
        pathname = pointLayerNameToCheck + ".shp"
        path = os.path.join(self.globalCourseDirectory, pathname)
        path = os.path.abspath(path)
        #print "Path: ", path
        
        #path = self.globalCourseDirectory + "\\" + pointLayerNameToCheck + ".shp"
        writer = QgsVectorFileWriter(path, "CP1250", fields, QGis.WKBPoint,
                                     coordinateSystem, "ESRI Shapefile")

        if writer.hasError() != QgsVectorFileWriter.NoError:
            #print "Error when creating shapefile: ",  writer.errorMessage()

        # Get an ordered list of SP, TP and FP - and reverse it
        orderedList = self.getOrderedFeatureListFromLayer()
        orderedList.reverse()
        maxLeg = -1
        currentOrderedListIndex = 0
        leg = 1
        number = 0
        for feature in orderedList:
            if feature.attribute('Leg') > maxLeg and feature.attribute('Leg') != None:
                maxLeg = feature.attribute('Leg')
        originalLeg = maxLeg
        
        for feature in orderedList:
            if feature.attribute('Category') != 'SP': # SP now the last item...
                startPoint = feature.geometry().asPoint()
                endPoint = orderedList[currentOrderedListIndex+1].geometry().asPoint()
                bearing = self.calculateBearing(startPoint,endPoint)
                distance = self.haversinePoints(startPoint,endPoint)
                # Add SP or TP
                cat = feature.attribute('Category')
                if feature.attribute('Category') == 'FP':
                    cat = 'SP'
                    number = 0
                #fet = QgsFeature() # feature
                fet = feature
                #print 'Cat: ', cat, 'Descr: ', feature.attribute('Descr'), 'LblLat: ', feature.attribute('LblLat'), 'LblLong: ', feature.attribute('LblLong')
                attrs = ([ cat, leg, number, feature.attribute('Descr'), feature.attribute('LblLat'),
                         feature.attribute('LblLong'), feature.attribute('LblRot'), bearing, distance ])
                fet.setAttributes(attrs)
                #fet.setGeometry(feature.geometry())
                #print 'fet.attribute Category: ', fet.attribute('Category')
                writer.addFeature(fet)
                
                # Add Secret Checkpoints for this leg
                #print 'originalLeg: ', originalLeg
                orderedListOfSC = self.getOrderedListOfSCForLeg(originalLeg)
                orderedListOfSC.reverse()
                scNumber = 1
                for scFeature in orderedListOfSC:
                    #print 'Cat: ', cat, 'Descr: ', scFeature.attribute('Descr'), 'LblLat: ', scFeature.attribute('LblLat'), 'LblLong: ', scFeature.attribute('LblLong')
                    fet = scFeature
                    attrs = ([ scFeature.attribute('Category'), leg, scNumber, scFeature.attribute('Descr'),
                             scFeature.attribute('LblLat'), scFeature.attribute('LblLong'),
                             scFeature.attribute('LblRot'), scFeature.attribute('OutbTT'),
                             scFeature.attribute('DistToNext') ])
                    fet.setAttributes(attrs)
                    #fet.setGeometry(scFeature.geometry())
                    writer.addFeature(fet)
                    scNumber = scNumber +1
                 
            elif feature.attribute('Category') == 'SP': # SP now the last item...
                cat = 'FP'
                number = None
                fet = feature
                attrs = ([ cat, leg, number, feature.attribute('Descr'), feature.attribute('LblLat'),
                         feature.attribute('LblLong'), feature.attribute('LblRot'),
                         feature.attribute('OutbTT'), feature.attribute('DistToNext') ])
                fet.setAttributes(attrs)
                #fet.setGeometry(feature.geometry())
                writer.addFeature(fet)
                number = 0

            
            currentOrderedListIndex = currentOrderedListIndex +1
            number = number +1
            originalLeg = originalLeg -1
            leg = leg +1

        # delete the writer to flush features to disk
        del writer

        resultCode = self.doesReverseCourseLayerExist(self.selectedLayerGlobal)
        #print resultCode
        if resultCode == 2:
            #print "Layer already exists in legend!"
            self.iface.messageBar().pushMessage("Error", "A reverse course for this course already exists! Backup/Delete Shapefile first, before you can create a new reverse course!", level=QgsMessageBar.CRITICAL, duration=30)
            return
        elif resultCode == 1:
            #print "Layer exists, but is not loaded (yet)!"
            #Load the layer first, then update the CourseLineLayer instead of creating a new file
            self.loadCourseLayer(self.selectedLayerGlobal)
            return
        elif resultCode == 3:
            #print "Wrong Layername?"
            return
        elif resultCode == 0:
            #print "Layer does not exist!"
            #Lets go ahead and create a new file!
        elif resultCode == 99:
            #print "Uh uh!"
            #Something went wrong, should we fix it?
            return
        resultCode = -1
        
    def updateCourseLines(self):
        #print "Lets go ahead and update an existing CourseLineLayer"

    
    def createLinesBetweenPoints(self, startPoint, endPoint):
        pass
    
    def createPointWithDistanceAndBearingFromPoint(self, startPoint, distance, bearing):
        radius = 6366710 # Earth radius in metres (6371000)
        distance = float(distance)
        bearingRad = math.radians(bearing)
        latRadStart = math.radians(startPoint.y())
        lonRadStart = math.radians(startPoint.x())
        latRadDest = (math.asin(math.sin(latRadStart) * math.cos(distance/radius) +
                      math.cos(latRadStart) * math.sin(distance/radius) * math.cos(bearingRad)))

        #lonRadDest = (lonRadStart + math.atan2(math.sin(bearingRad) * math.sin(distance/radius) *
                      #math.cos(latRadStart), math.cos(distance/radius) - math.sin(latRadStart) *
                      #math.sin(latRadDest)))

        dlonRadDest = (math.atan2(math.sin(bearingRad) * math.sin(distance/radius) *
                       math.cos(latRadStart), math.cos(distance/radius) -
                       math.sin(latRadStart) * math.sin(latRadDest)))
        lonRadDest = ((lonRadStart+dlonRadDest+math.pi)%(2*math.pi))-math.pi
        latDegDest = math.degrees(latRadDest)
        lonDegDest = math.degrees(lonRadDest)
        #lonDegDest = (lonDegDest+540)%360-180
        #print "lonDegDest Signed: ", lonDegDest
        destinationPoint = QgsPoint(lonDegDest,latDegDest)
        return destinationPoint
    
    def randomizeSecretCheckpoints (self):
        self.updateSettings()
        orderedList = self.getOrderedFeatureListFromLayer()
        crs = self.selectedLayerGlobal.crs()
        d = QgsDistanceArea()
        d.setSourceCrs(crs) #WGS84
        d.setEllipsoid(crs.ellipsoidAcronym())
        d.setEllipsoidalMode(crs.geographicFlag())
        
        currentOrderedListIndex = 0
        leg = 1
        for feature in orderedList:
            currentFeatureIndex = feature.id()
            #print feature.attribute('Category')
            if feature.attribute('Category') != 'FP':
                point01 = feature.geometry().asPoint()
                point02 = orderedList[currentOrderedListIndex+1].geometry().asPoint()
                calcDist = self.haversinePoints(point01,point02)
                calcOutboundSigned = d.bearing(point01, point02) * 180/math.pi#Convert to Degrees
                calcOutbound = 0
                if calcOutboundSigned < 0:
                    calcOutbound = 360 + calcOutboundSigned
                else:
                    calcOutbound = calcOutboundSigned
                
                # NOTE! This function is not completed, because the function exists in PFCM
                
                #Randomize two Secret Checkpoints per leg (Riksnav)
                #random.uniform()
                
                #caps = self.selectedLayerGlobal.dataProvider().capabilities()
                #if caps & QgsVectorDataProvider.ChangeAttributeValues:
                    #attrs = { feature.fieldNameIndex('Leg') : leg, feature.fieldNameIndex('OutbTT') : calcOutbound, feature.fieldNameIndex('DistToNext') : calcDist }
                    #self.selectedLayerGlobal.dataProvider().changeAttributeValues({ currentFeatureIndex : attrs })

                
            currentOrderedListIndex = currentOrderedListIndex +1
            leg = leg +1

    def moveAllSCToCourseline(self):
        self.updateSettings()
        orderedList = self.getOrderedFeatureListFromLayer()
        crs = self.selectedLayerGlobal.crs()
        d = QgsDistanceArea()
        d.setSourceCrs(crs) #WGS84
        d.setEllipsoid(crs.ellipsoidAcronym())
        d.setEllipsoidalMode(crs.geographicFlag())
        
        currentOrderedListIndex = 0
        leg = 1
        for feature in orderedList:
            currentFeatureIndex = feature.id()
            #print feature.attribute('Category')
            if feature.attribute('Category') != 'FP':
                # Calculate Distance and Bearing for the leg as usual!
                point01 = feature.geometry().asPoint()
                point02 = orderedList[currentOrderedListIndex+1].geometry().asPoint()
                calcDist = self.haversinePoints(point01,point02)
                calcOutboundSigned = d.bearing(point01, point02) * 180/math.pi#Convert to Degrees
                calcOutbound = 0
                if calcOutboundSigned < 0:
                    calcOutbound = 360 + calcOutboundSigned
                else:
                    calcOutbound = calcOutboundSigned
                
                # Get a sorted list of Secret Checkpoints for the current leg
                legFromFeature = int(feature.attribute('Leg'))
                if legFromFeature is not NULL:
                    if leg == legFromFeature:
                        listSC = self.getOrderedListOfSCForLeg(leg)
                        for sc in listSC:
                            # Calculate distance from start of leg
                            scdist = self.haversinePoints(point01,sc.geometry().asPoint())
                            #print "scdist: ", scdist
                            scdistmeters = scdist * 1852
                            # Create a point ON the line
                            newSCPoint = self.createPointWithDistanceAndBearingFromPoint(point01,scdistmeters,calcOutbound)
                            # Update SC in Coursepointlayer
                            fid = sc.id()
                            caps = self.selectedLayerGlobal.dataProvider().capabilities()
                            if caps & QgsVectorDataProvider.ChangeGeometries:
                                geom = QgsGeometry.fromPoint(newSCPoint)
                                self.selectedLayerGlobal.dataProvider().changeGeometryValues({ fid : geom })

                
            currentOrderedListIndex = currentOrderedListIndex +1
            leg = leg +1
        self.iface.mapCanvas().refresh()
    
    def testFunction(self):
        startPoint = QgsPoint(13.69976979,55.6534368)
        endPoint = QgsPoint(14.03198015,55.65110134)
        distance = 1.0 * 1852 # In metres
        bearing = 90.575
        returnedPoint = self.createPointWithDistanceAndBearingFromPoint(startPoint, distance, bearing)
        #print returnedPoint
    
    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/PFCCourse/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'1. Settings'),
            callback=self.settings,
            add_to_toolbar=False,
            parent=self.iface.mainWindow())

        self.add_action(
            icon_path,
            text=self.tr(u'2. Calculate Distance And Bearings'),
            callback=self.calcDistBear,
            add_to_toolbar=False,
            parent=self.iface.mainWindow())

        self.add_action(
            icon_path,
            text=self.tr(u'3. Create Courselines'),
            callback=self.createCourseLines,
            add_to_toolbar=False,
            parent=self.iface.mainWindow())
        
        self.add_action(
            icon_path,
            text=self.tr(u'4. Update/Move Secret Checkpoints to Courselines'),
            callback=self.moveAllSCToCourseline,
            add_to_toolbar=False,
            parent=self.iface.mainWindow())
        
        self.add_action(
            icon_path,
            text=self.tr(u'5. Write Fugawifile'),
            callback=self.writeFugawiFile,
            add_to_toolbar=False,
            parent=self.iface.mainWindow())
        
        self.add_action(
            icon_path,
            text=self.tr(u'6. Create Reverse Course'),
            callback=self.createReverseCourse,
            add_to_toolbar=False,
            parent=self.iface.mainWindow())

        #self.add_action(
            #icon_path,
            #text=self.tr(u'9. Test Function'),
            #callback=self.testFunction,
            #add_to_toolbar=False,
            #parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&PFC Course Builder'),
                action)
            
            #No toolbar for now...
            #self.iface.removeToolBarIcon(action)
        # remove the toolbar
        #del self.toolbar


    def run(self):
        """Run method that performs all the real work"""
        layers = self.iface.legendInterface().layers()
        layer_list = []
        for layer in layers:
            if layer.type() == 0:#VectorLayer = 0
                if layer.geometryType() == 0:#Pointlayer
                    layer_list.append(layer.name())

        self.dlg.comboBoxLayer.addItems(layer_list)

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
                    #Hämta valt lager
            layers = self.iface.legendInterface().layers()
            selectedLayerIndex = self.dlg.comboBoxLayer.currentIndex()
            selectedLayer = layers[selectedLayerIndex]
            self.selectedLayerGlobal = selectedLayer
            #print selectedLayer
            #print self.selectedLayerGlobal

    def select_courses_directory(self):
        #courseDirectory = str(QFileDialog.getExistingDirectory(self.sdlg, "Select Directory", self.globalCourseDirectory))
        courseDirectory = unicode(QFileDialog.getExistingDirectory(self.sdlg, "Select Directory", self.globalCourseDirectory))
        #courseDirectory = QFileDialog.getOpenFileName(self.sdlg, "Choose file..")
        self.sdlg.lineEditDirectory.setText(courseDirectory)
    
    def settings(self):
        """Run method that performs all the real work"""

        # See if we already have a CourseDirectory setting
        sp = QgsProject.instance()
        sptext = sp.readEntry("PFCCourse", "CourseDirectory", "C:\\")[0]
        self.sdlg.lineEditDirectory.setText(sptext)
        self.globalCourseDirectory = sptext
        
        # See if we have a Pointlayer saved
        spcp = sp.readEntry("PFCCourse", "CoursePointlayer", "")[0]
        #print 'Updating Combo Box'
        layers = self.iface.legendInterface().layers()
        #layers = QgsMapLayerRegistry.instance().mapLayers()
        layer_list = []
        actualLayersList = []
        for layer in layers:
            if layer.type() == 0:#VectorLayer = 0
                if layer.geometryType() == 0:#Pointlayer
                    layer_list.append(layer.name()) # Just for text
                    actualLayersList.append(layer)

        comboIndex = 0
        if not spcp == "":
            #print "spcp has content: ", spcp
            comboIndex = layer_list.index(spcp) if spcp in layer_list else -1
        #Rensa först
        #self.sdlg.comboBoxCourselayer.clear() tillagd för att rensa droplisten, varje gång.
        self.sdlg.comboBoxCourselayer.clear()
        self.sdlg.comboBoxCourselayer.addItems(layer_list)
        self.sdlg.comboBoxCourselayer.setCurrentIndex(comboIndex)
        
        # show the dialog
        self.sdlg.show()
        # Run the dialog event loop
        result = self.sdlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            #layers = self.iface.legendInterface().layers()
            selectedLayerIndex = self.sdlg.comboBoxCourselayer.currentIndex()
            selectedLayerName = unicode(self.sdlg.comboBoxCourselayer.currentText())
            #print "Current index is: ", str(selectedLayerIndex), 'selectedLayerName: ', selectedLayerName
            #selectedLayer = actualLayersList[selectedLayerIndex]
            selectedLayer = QgsMapLayerRegistry.instance().mapLayersByName(selectedLayerName)[0]
            self.selectedLayerGlobal = selectedLayer
            #print 'Layer: ', self.selectedLayerGlobal.name()

            courseDirectory = self.sdlg.lineEditDirectory.text()
            proj = QgsProject.instance()
            
            # store values
            proj.writeEntry("PFCCourse", "CourseDirectory", courseDirectory)
            proj.writeEntry("PFCCourse", "CoursePointlayer", selectedLayer.name())

            # read values
            mytext = proj.readEntry("PFCCourse", "CourseDirectory", "C:\\")[0]
            #print mytext

    def updateSettings(self):
        # Global CourseDirectory
        # See if we already have a CourseDirectory setting
        sp = QgsProject.instance()
        spcd = sp.readEntry("PFCCourse", "CourseDirectory", "C:\\")[0]
        self.globalCourseDirectory = spcd

        # Global Layer Pointer - Start with selected
        spcp = sp.readEntry("PFCCourse", "CoursePointlayer", "")[0]
        #print "CoursePointlayer from Settings: ", spcp
        if spcp == "":
            self.selectedLayerGlobal = self.iface.legendInterface().currentLayer()#Choose current instead
        else:
            self.selectedLayerGlobal = QgsMapLayerRegistry.instance().mapLayersByName(spcp)[0]
