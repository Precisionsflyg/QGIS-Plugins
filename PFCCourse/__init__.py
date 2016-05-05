# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PFCCourse
                                 A QGIS plugin
 Builds a course for Precision Flying Competitions
                             -------------------
        begin                : 2016-04-17
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
    """Load PFCCourse class from file PFCCourse.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .pfccourse import PFCCourse
    return PFCCourse(iface)
