# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright (C) 2020, GEM Foundation
#
# OpenQuake is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OpenQuake is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with OpenQuake.  If not, see <http://www.gnu.org/licenses/>.

import os
import pathlib
import unittest
import numpy
from openquake.hazardlib.geo import Point, Line
from openquake.hazardlib.geo.mesh import Mesh
from openquake.hazardlib.geo.geodetic import geodetic_distance
from openquake.hazardlib.geo.surface.kite_fault import KiteSurface
from openquake.hazardlib.geo.surface.multi import MultiSurface

cd = pathlib.Path(__file__).parent
aac = numpy.testing.assert_allclose


class MultiSurfaceTestCase(unittest.TestCase):
    # Test multiplanar surfaces used in UCERF, which are build from
    # pre-exiting multisurfaces. In this test there are 3 original
    # multisurfaces (from sections 18, 19, 20) and a reference point;
    # the rjb distances are 51.610675, 54.441119, -60.205692 respectively;
    # then two multisurfaces are built (a from 18+19, b from 19+20)
    # and distances recomputed; as expected for the rjb distances one gets
    # rjb(18+19) = min(rjb(18), rjb(19)) and same for 19+20.
    # This is NOT true for rx distances.

    def test_rjb(self):
        mesh = Mesh(numpy.array([-118.]), numpy.array([33]))   # 1 point
        tmp = os.path.join('data', 'msurface18.csv')
        surf18 = MultiSurface.from_csv(cd / tmp)  # 2 planes
        tmp = os.path.join('data', 'msurface19.csv')
        surf19 = MultiSurface.from_csv(cd / tmp)  # 2 planes
        tmp = os.path.join('data', 'msurface20.csv')
        surf20 = MultiSurface.from_csv(cd / tmp)  # 1 plane
        rjb18 = surf18.get_joyner_boore_distance(mesh)[0]
        rjb19 = surf19.get_joyner_boore_distance(mesh)[0]
        rjb20 = surf20.get_joyner_boore_distance(mesh)[0]
        aac([rjb18, rjb19, rjb20], [85.676294, 89.225542, 92.937021])

        surfa = MultiSurface(surf18.surfaces + surf19.surfaces)
        surfb = MultiSurface(surf19.surfaces + surf20.surfaces)
        rjba = surfa.get_joyner_boore_distance(mesh)[0]
        rjbb = surfb.get_joyner_boore_distance(mesh)[0]
        aac([rjba, rjbb], [85.676294, 89.225542])

    def test_rx(self):
        mesh = Mesh(numpy.array([-118.]), numpy.array([33]))   # 1 point
        tmp = os.path.join('data', 'msurface18.csv')
        surf18 = MultiSurface.from_csv(cd / tmp)  # 2 planes
        tmp = os.path.join('data', 'msurface19.csv')
        surf19 = MultiSurface.from_csv(cd / tmp)  # 2 planes
        tmp = os.path.join('data', 'msurface20.csv')
        surf20 = MultiSurface.from_csv(cd / tmp)  # 1 plane
        rx18 = surf18.get_rx_distance(mesh)[0]
        rx19 = surf19.get_rx_distance(mesh)[0]
        rx20 = surf20.get_rx_distance(mesh)[0]
        aac([rx18, rx19, rx20], [51.610675, 54.441119, -60.205692])

        surfa = MultiSurface(surf18.surfaces + surf19.surfaces)
        surfb = MultiSurface(surf19.surfaces + surf20.surfaces)
        rxa = surfa.get_rx_distance(mesh)[0]
        rxb = surfb.get_rx_distance(mesh)[0]
        aac([rxa, rxb], [53.034889, -56.064366])

    def test_rx_kite(self):
        spc = 2.0
        pro1 = Line([Point(0.2, 0.0, 0.0), Point(0.2, 0.05, 15.0)])
        pro2 = Line([Point(0.0, 0.0, 0.0), Point(0.0, 0.05, 15.0)])
        sfc1 = KiteSurface.from_profiles([pro1, pro2], spc, spc)
        msurf = MultiSurface([sfc1])
        pcoo = numpy.array([[0.2, 0.1], [0.0, -0.1]])
        mesh = Mesh(pcoo[:, 0], pcoo[:, 1])
        # Compute expected distances
        lo = pro1.points[0].longitude
        la = pro1.points[0].longitude
        tmp0 = geodetic_distance(lo, la, pcoo[0, 0], pcoo[0, 1])
        lo = pro2.points[0].longitude
        la = pro2.points[0].longitude
        tmp1 = geodetic_distance(lo, la, pcoo[1, 0], pcoo[1, 1])
        # Checking
        rx = msurf.get_rx_distance(mesh)
        expected = numpy.array([tmp0, -tmp1])
        numpy.testing.assert_almost_equal(expected, rx, decimal=5)
