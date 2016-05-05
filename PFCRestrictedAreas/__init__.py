# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PrecisionFlying
                                 A QGIS plugin
 Tools for creating  maps for precision flying competitions.
                             -------------------
        begin                : 2016-04-10
        copyright            : (C) 2016 by Joakim Mårtensson
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
    """Load PrecisionFlying class from file PrecisionFlying.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .precision_flying import PrecisionFlying
    return PrecisionFlying(iface)
