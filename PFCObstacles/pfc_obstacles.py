# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PFCObstacles
                                 A QGIS plugin
 Import Obstacles
                              -------------------
        begin                : 2016-04-11
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Joakim Maartensson
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
from pfc_obstacles_dialog import PFCObstaclesDialog
import os.path


class PFCObstacles:
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
            'PFCObstacles_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = PFCObstaclesDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&PFC Obstacles')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'PFCObstacles')
        self.toolbar.setObjectName(u'PFCObstacles')

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
        return QCoreApplication.translate('PFCObstacles', message)


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

    def convertDMS2DD(self, DMS):
        if DMS.endswith('N'):
            print "Norr hittad, DMS: ", DMS
            lengthOfCoord = len(DMS)
            maxSliceIndex = lengthOfCoord -1
            DD = DMS[0:2]
            MM = DMS[2:4]
            SS = DMS[4:maxSliceIndex]
            dFloat = float(DD)
            mFloat = float(MM)
            sFloat = float(SS)
        
            #Konvertera till decimalgrader
            decimalDegrees = dFloat + (mFloat / 60) + (sFloat / 3600)
            print decimalDegrees
            return decimalDegrees
        
        elif DMS.endswith('S'):
            print "Syd hittad, DMS: ", DMS
            lengthOfCoord = len(DMS)
            maxSliceIndex = lengthOfCoord -1
            DD = DMS[0:2]
            MM = DMS[2:4]
            SS = DMS[4:maxSliceIndex]
            dFloat = float(DD)
            mFloat = float(MM)
            sFloat = float(SS)
        
            #Konvertera till decimalgrader
            decimalDegrees = -(dFloat + (mFloat / 60) + (sFloat / 3600))
            print decimalDegrees
            return decimalDegrees
        
        elif DMS.endswith('E'):
            #Kontrollera att strängen innehåller 8 tecken...
            print "Öst hittad, DMS: ", DMS
            lengthOfCoord = len(DMS)
            maxSliceIndex = lengthOfCoord -1
            DD = DMS[0:3]
            MM = DMS[3:5]
            SS = DMS[5:maxSliceIndex]
            dFloat = float(DD)
            mFloat = float(MM)
            sFloat = float(SS)
        
            #Konvertera till decimalgrader
            decimalDegrees = dFloat + (mFloat / 60) + (sFloat / 3600)
            print decimalDegrees
            return decimalDegrees
        
        elif DMS.endswith('W'):
            print "Väst hittad, DMS: ", DMS
            lengthOfCoord = len(DMS)
            maxSliceIndex = lengthOfCoord -1
            DD = DMS[0:3]
            MM = DMS[3:5]
            SS = DMS[5:maxSliceIndex]
            dFloat = float(DD)
            mFloat = float(MM)
            sFloat = float(SS)
        
            #Konvertera till decimalgrader
            decimalDegrees = -(dFloat + (mFloat / 60) + (sFloat / 3600))
            print decimalDegrees
            return decimalDegrees
        
    def addObstacles(self):
        
        #stringNorth = self.dlg.lineEditNorth.text()
        northDD = self.convertDMS2DD(self.dlg.lineEditNorth.text())
        eastDD = self.convertDMS2DD(self.dlg.lineEditEast.text())
        
        #Hämta valt lager
        layers = self.iface.legendInterface().layers()
        selectedLayerIndex = self.dlg.comboBoxLayer.currentIndex()
        selectedLayer = layers[selectedLayerIndex]
 
            
        caps = selectedLayer.dataProvider().capabilities()
        #caps_string = selectedLayer.dataProvider().capabilitiesString()
        #print caps_string

        if caps & QgsVectorDataProvider.AddFeatures:
            feat = QgsFeature(selectedLayer.pendingFields())
            feat.setAttribute('No',self.dlg.lineEditNumber.text())
            feat.setAttribute('Designatio',self.dlg.lineEditName.text())
            feat.setAttribute('Height ft',self.dlg.lineEditHeight.text())
            feat.setAttribute('Elev ft',self.dlg.lineEditElevation.text())
            feat.setAttribute('Light Char',self.dlg.lineEditLights.text())
            feat.setAttribute('Types of o',self.dlg.lineEditObstacleType.text())
            feat.setAttribute('Visible',"Y")
            feat.setAttribute('LblVis',"1")
            geoPoint = QgsPoint(eastDD,northDD)
            feat.setGeometry(QgsGeometry.fromPoint(geoPoint))
            (res, outFeats) = selectedLayer.dataProvider().addFeatures([feat])
            #self.iface.mapCanvas().refresh()

    def refresh_layers(self):
        for layer in self.iface.mapCanvas().layers():
            layer.triggerRepaint()

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/PFCObstacles/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Obstacles'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&PFC Obstacles'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""
        layers = self.iface.legendInterface().layers()
        layer_list = []
        for layer in layers:
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
            self.addObstacles()
            self.dlg.lineEditNumber.clear()
            self.dlg.lineEditName.clear()
            self.dlg.lineEditNorth.clear()
            self.dlg.lineEditEast.clear()
            self.dlg.lineEditHeight.clear()
            self.dlg.lineEditElevation.clear()
            self.dlg.lineEditLights.clear()
            self.dlg.lineEditObstacleType.clear()
            self.dlg.textEditPastebin.clear()
            self.refresh_layers()

