# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PFCObstacles
                                 A QGIS plugin
 Import Obstacles
                             -------------------
        begin                : 2016-04-11
        copyright            : (C) 2016 by Joakim Maartensson
        email                : calder2@telia.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load PFCObstacles class from file PFCObstacles.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .pfc_obstacles import PFCObstacles
    return PFCObstacles(iface)
