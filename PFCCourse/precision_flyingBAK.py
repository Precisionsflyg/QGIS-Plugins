# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PrecisionFlying
                                 A QGIS plugin
 Tools for creating  maps for precision flying competitions.
                              -------------------
        begin                : 2016-04-10
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
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from precision_flying_dialog import PrecisionFlyingDialog
import os.path


class PrecisionFlying:
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
            'PrecisionFlying_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = PrecisionFlyingDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Precision Flying Competition')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'PrecisionFlying')
        self.toolbar.setObjectName(u'PrecisionFlying')

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
        return QCoreApplication.translate('PrecisionFlying', message)


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

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        icon_path = ':/plugins/PrecisionFlying/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Controlled Airspaces'),
            callback=self.run,
            parent=self.iface.mainWindow())



    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Precision Flying Competition'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def addRestrictionArea(self):
        #inString = '''554632N 0140547E - 554609N 0140954E -
        #554514N 0140819E - 554319N 0140919E -
        #554325N 0141146E - 554204N 0140717E -
        #554507N 0140358E - 554632N 0140547E'''
        inString = self.dlg.textEditLateral.toPlainText()
        inList = inString.split('-')
        noOfCoords = len(inList)

        coordinateArrayDMS = [None] * noOfCoords
        for i in range(noOfCoords):
            coordinateArrayDMS[i] = [None] * 2

        for i in range(noOfCoords):
            coordinateArrayDMS[i] = inList[i].split()

        coordinateArrayDD = [None] * noOfCoords
        for i in range(noOfCoords):
            coordinateArrayDD[i] = [None] * 2

        for i in range(noOfCoords):
            if coordinateArrayDMS[i][0].endswith('N'):
                #Nordkoordinat hittad
                lengthOfCoord = len(coordinateArrayDMS[i][0])
                maxSliceIndex = lengthOfCoord -1
                DD = coordinateArrayDMS[i][0][0:2]
                MM = coordinateArrayDMS[i][0][2:4]
                SS = coordinateArrayDMS[i][0][4:maxSliceIndex]
                dFloat = float(DD)
                mFloat = float(MM)
                sFloat = float(SS)
        
                #Konvertera till decimalgrader
                decimalDegrees = dFloat + (mFloat / 60) + (sFloat / 3600)
                coordinateArrayDD[i][0] = decimalDegrees
        #        print coordinateArrayDD[i][0]
        
            elif coordinateArrayDMS[i][0].endswith('S'):
                #Sydkoordinat hittad
                lengthOfCoord = len(coordinateArrayDMS[i][0])
                maxSliceIndex = lengthOfCoord -1
                DD = coordinateArrayDMS[i][0][0:2]
                MM = coordinateArrayDMS[i][0][2:4]
                SS = coordinateArrayDMS[i][0][4:maxSliceIndex]
                dFloat = float(DD)
                mFloat = float(MM)
                sFloat = float(SS)
        
                #Konvertera till decimalgrader
                decimalDegrees = -(dFloat + (mFloat / 60) + (sFloat / 3600))
                coordinateArrayDD[i][0] = decimalDegrees
        #        print coordinateArrayDD[i][0]

        for i in range(noOfCoords):
            if coordinateArrayDMS[i][1].endswith('E'):
                #Ostkoordinat hittad
                lengthOfCoord = len(coordinateArrayDMS[i][1])
                maxSliceIndex = lengthOfCoord -1
                DD = coordinateArrayDMS[i][1][0:3]
                MM = coordinateArrayDMS[i][1][3:5]
                SS = coordinateArrayDMS[i][1][5:maxSliceIndex]
                dFloat = float(DD)
                mFloat = float(MM)
                sFloat = float(SS)
        
                #Konvertera till decimalgrader
                decimalDegrees = dFloat + (mFloat / 60) + (sFloat / 3600)
                coordinateArrayDD[i][1] = decimalDegrees
        #        print coordinateArrayDD[i][1]
        
            elif coordinateArrayDMS[i][1].endswith('W'):
                #Vaestkoordinat hittad
                lengthOfCoord = len(coordinateArrayDMS[i][1])
                maxSliceIndex = lengthOfCoord -1
                DD = coordinateArrayDMS[i][1][0:3]
                MM = coordinateArrayDMS[i][1][3:5]
                SS = coordinateArrayDMS[i][1][5:maxSliceIndex]
                dFloat = float(DD)
                mFloat = float(MM)
                sFloat = float(SS)
        
                #Konvertera till decimalgrader
                decimalDegrees = -(dFloat + (mFloat / 60) + (sFloat / 3600))
                coordinateArrayDD[i][1] = decimalDegrees
        #        print coordinateArrayDD[i][1]


        print coordinateArrayDMS
        print coordinateArrayDD

        #Skriv till aktivt lager
        #layer = iface.activeLayer()
        
        #Hämta R, P eller D-område
        areaCategoryIndex = self.dlg.comboBoxType.currentIndex()
        areaCategory = "R"
        print areaCategoryIndex
        if areaCategoryIndex == 0:
            areaCategory = "R"
        elif areaCategoryIndex == 1:
            areaCategory = "P"
        elif areaCategoryIndex == 2:
            areaCategory = "D"
        else:
            areaCategory = "U"
        
        #Hämta valt lager
        layers = self.iface.legendInterface().layers()
        selectedLayerIndex = self.dlg.comboBoxLayer.currentIndex()
        selectedLayer = layers[selectedLayerIndex]
 
        iter = selectedLayer.getFeatures()
        highestID = 0

        for feature in iter:
            # retrieve every feature with its geometry and attributes
            # fetch geometry
            geom = feature.geometry()
            #print "Feature ID %d: " % feature.id()

            # show some information about the feature
            if geom.type() == QGis.Polygon:
                x = geom.asPolygon()
#                numPts = 0
#                for ring in x:
#                    numPts += len(ring)
#                print "Polygon: %d rings with %d points" % (len(x), numPts)
            else:
                print "Unknown"

            # fetch attributes
            attrs = feature.attributes()

            # attrs is a list. It contains all the attribute values of this feature
            print attrs
            currentID = attrs[0]
            if currentID >= highestID:
                highestID = currentID
            #print highestID
            
        caps = selectedLayer.dataProvider().capabilities()
        #caps_string = selectedLayer.dataProvider().capabilitiesString()
        #print caps_string

        if caps & QgsVectorDataProvider.AddFeatures:
            feat = QgsFeature(selectedLayer.pendingFields())
            feat.setAttribute('id',highestID+1)
            #print highestID
            feat.setAttribute('Ident',self.dlg.lineEditIdent.text())
            feat.setAttribute('Name',self.dlg.lineEditName.text())
            feat.setAttribute('Remarks',self.dlg.textEditRemarks.toPlainText())
            feat.setAttribute('Upper',self.dlg.lineEditUpper.text())
            feat.setAttribute('Lower',self.dlg.lineEditLower.text())
            feat.setAttribute('Cat',areaCategory)
            points = [None] * noOfCoords
            for i in range(noOfCoords):
                #Använder LatLon i array, men QGIS använder LonLat...
                points[i] = QgsPoint(coordinateArrayDD[i][1],coordinateArrayDD[i][0])
                #print points[i]
            feat.setGeometry(QgsGeometry.fromPolygon([points]))
            (res, outFeats) = selectedLayer.dataProvider().addFeatures([feat])
            #self.iface.mapCanvas().refresh()

    def refresh_layers(self):
        for layer in self.iface.mapCanvas().layers():
            layer.triggerRepaint()

    def run(self):
        """Run method that performs all the real work"""
        layers = self.iface.legendInterface().layers()
        layer_list = []
        for layer in layers:
            layer_list.append(layer.name())

        self.dlg.comboBoxLayer.addItems(layer_list)
        
        comboBoxTypeList = ["Restricted Area","Prohibited Area","Danger Area"]
        self.dlg.comboBoxType.clear()
        self.dlg.comboBoxType.addItems(comboBoxTypeList)
		
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            self.addRestrictionArea()
            self.dlg.lineEditIdent.clear()
            self.dlg.lineEditLower.clear()
            self.dlg.lineEditName.clear()
            self.dlg.lineEditUpper.clear()
            self.dlg.textEditLateral.clear()
            self.dlg.textEditRemarks.clear()
            self.refresh_layers()
 