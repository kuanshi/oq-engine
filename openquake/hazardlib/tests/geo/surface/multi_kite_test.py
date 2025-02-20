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
import unittest
import numpy as np
import matplotlib.pyplot as plt
from openquake.hazardlib.geo.geodetic import (
    geodetic_distance, npoints_towards)
from openquake.hazardlib.geo.mesh import Mesh
from openquake.hazardlib.tests.geo.surface.kite_fault_test import (
    _read_profiles)
from openquake.hazardlib.geo import Point, Line
from openquake.hazardlib.geo.surface.multi import MultiSurface
from openquake.hazardlib.geo.surface.kite_fault import KiteSurface
from openquake.hazardlib.tests.geo.surface.kite_fault_test import plot_mesh_2d

BASE_PATH = os.path.dirname(__file__)
BASE_DATA_PATH = os.path.join(BASE_PATH, 'data')
PLOTTING = False
OVERWRITE = False

aae = np.testing.assert_almost_equal


class MultiSurfaceOneTestCase(unittest.TestCase):

    def setUp(self):
        # First surface - Almost vertical dipping to south
        prf1 = Line([Point(0, 0, 0), Point(0, -0.00001, 20.)])
        prf2 = Line([Point(0.15, 0, 0), Point(0.15, -0.00001, 20.)])
        prf3 = Line([Point(0.3, 0, 0), Point(0.3, -0.00001, 20.)])
        sfca = KiteSurface.from_profiles([prf1, prf2, prf3], 1., 1.)
        self.msrf = MultiSurface([sfca])

    def test_get_width(self):
        # Surface is almost vertical. The width must be equal to the depth
        # difference between the points at the top and bottom
        width = self.msrf.get_width()
        msg = 'Multi fault surface: width is wrong'
        self.assertAlmostEqual(20.0, width, places=2, msg=msg)

    def test_get_dip(self):
        # Surface is almost vertical. The dip must be equal to 90
        dip = self.msrf.get_dip()
        msg = 'Multi fault surface: dip is wrong'
        self.assertAlmostEqual(90.0, dip, places=2, msg=msg)

    def test_get_area(self):
        computed = self.msrf.get_area()
        length = geodetic_distance(0.0, 0.0, 0.3, 0.0)
        expected = length * 20.0
        perc_diff = abs(computed - expected) / computed * 100
        msg = 'Multi fault surface: area is wrong'
        self.assertTrue(perc_diff < 2, msg=msg)

    def test_get_area1(self):
        pntsa = npoints_towards(lon=0.32, lat=0.0, depth=0.0, azimuth=45,
                                hdist=10.0, vdist=0.0, npoints=2)
        pntsb = npoints_towards(lon=pntsa[0][1], lat=pntsa[1][1],
                                depth=pntsa[2][1], azimuth=45+90,
                                hdist=10.0, vdist=10.0, npoints=2)
        pntsc = npoints_towards(lon=0.32, lat=0.0, depth=0.0, azimuth=45+90,
                                hdist=10.0, vdist=10.0, npoints=2)
        tmp = Point(pntsc[0][1], pntsc[1][1], pntsc[2][1])
        prf3 = Line([Point(0.32, 0, 0), tmp])
        tmp1 = Point(pntsa[0][1], pntsa[1][1], pntsa[2][1])
        tmp2 = Point(pntsb[0][1], pntsb[1][1], pntsb[2][1])
        prf4 = Line([tmp1, tmp2])
        sfcb = KiteSurface.from_profiles([prf3, prf4], 0.2, 0.2)

        computed = sfcb.get_area()
        expected = 10.0 * 14.14
        msg = 'Multi fault surface: area is wrong'
        aae(expected, computed, decimal=-1, err_msg=msg)


class MultiSurfaceTwoTestCase(unittest.TestCase):

    def setUp(self):

        # First surface - Almost vertical dipping to south
        prf1 = Line([Point(0, 0, 0), Point(0, -0.00001, 20.)])
        prf2 = Line([Point(0.15, 0, 0), Point(0.15, -0.00001, 20.)])
        prf3 = Line([Point(0.3, 0, 0), Point(0.3, -0.00001, 20.)])
        sfca = KiteSurface.from_profiles([prf1, prf2, prf3], 1., 1.)

        # Second surface - Strike to NE and dip to SE
        pntsa = npoints_towards(lon=0.32, lat=0.0, depth=0.0, azimuth=45,
                                hdist=10.0, vdist=0.0, npoints=2)
        pntsb = npoints_towards(lon=pntsa[0][1], lat=pntsa[1][1],
                                depth=pntsa[2][1], azimuth=45+90,
                                hdist=10.0, vdist=10.0, npoints=2)
        pntsc = npoints_towards(lon=0.32, lat=0.0, depth=0.0, azimuth=45+90,
                                hdist=10.0, vdist=10.0, npoints=2)
        tmp = Point(pntsc[0][1], pntsc[1][1], pntsc[2][1])
        prf3 = Line([Point(0.32, 0, 0), tmp])
        tmp1 = Point(pntsa[0][1], pntsa[1][1], pntsa[2][1])
        tmp2 = Point(pntsb[0][1], pntsb[1][1], pntsb[2][1])
        prf4 = Line([tmp1, tmp2])
        sfcb = KiteSurface.from_profiles([prf3, prf4], 0.2, 0.2)

        # Create surface and mesh needed for the test
        self.msrf = MultiSurface([sfca, sfcb])
        self.coo = np.array([[-0.1, 0.0], [0.0, 0.1]])
        self.mesh = Mesh(self.coo[:, 0], self.coo[:, 1])

    def test_areas(self):
        """ Compute the areas of surfaces """
        length = geodetic_distance(0.0, 0.0, 0.3, 0.0)
        expected = np.array([length * 20.0, 10 * 14.14])
        computed = self.msrf._get_areas()
        msg = 'Multi fault surface: areas are wrong'
        np.testing.assert_almost_equal(expected, computed, err_msg=msg,
                                       decimal=-1)

    def test_width(self):
        """ Compute the width of a multifault surface with 2 sections"""
        computed = self.msrf.get_width()
        # The width of the first surface is about 20 km while the second one
        # is about 14 km. The total width is the weighted mean of the width of
        # each section (weight proportional to the area)
        smm = np.sum(self.msrf.areas)
        expected = (20.0*self.msrf.areas[0] + 14.14*self.msrf.areas[1]) / smm
        perc_diff = abs(computed - expected) / computed * 100
        msg = f'Multi fault surface: width is wrong. % diff {perc_diff}'
        self.assertTrue(perc_diff < 0.2, msg=msg)

    def test_get_area(self):
        computed = self.msrf.get_area()
        length = geodetic_distance(0.0, 0.0, 0.3, 0.0)
        expected = length * 20.0 + 100
        perc_diff = abs(computed - expected) / computed
        msg = 'Multi fault surface: area is wrong'
        self.assertTrue(perc_diff < 0.1, msg=msg)


class MultiSurfaceWithNaNsTestCase(unittest.TestCase):

    NAME = 'MultiSurfaceWithNaNsTestCase'

    def setUp(self):
        path = os.path.join(BASE_DATA_PATH, 'profiles08')

        hsmpl = 2
        vsmpl = 2
        idl = False
        alg = False

        # Read the profiles with prefix cs_50. These profiles dip toward
        # north
        prf, _ = _read_profiles(path, 'cs_50')
        srfc50 = KiteSurface.from_profiles(prf, vsmpl, hsmpl, idl, alg)

        # Read the profiles with prefix cs_52. These profiles dip toward
        # north. This section is west to the section defined by cs_50
        prf, _ = _read_profiles(path, 'cs_51')
        srfc51 = KiteSurface.from_profiles(prf, vsmpl, hsmpl, idl, alg)

        clo = []
        cla = []
        step = 0.01
        for lo in np.arange(-71.8, -69, step):
            tlo = []
            tla = []
            for la in np.arange(19.25, 20.25, step):
                tlo.append(lo)
                tla.append(la)
            clo.append(tlo)
            cla.append(tla)
        self.clo = np.array(clo)
        self.cla = np.array(cla)
        mesh = Mesh(lons=self.clo.flatten(), lats=self.cla.flatten())

        # Define multisurface and mesh of sites
        self.srfc50 = srfc50
        self.srfc51 = srfc51

        self.msrf = MultiSurface([srfc50, srfc51])
        self.mesh = mesh

        self.los = [self.msrf.surfaces[0].mesh.lons,
                    self.msrf.surfaces[1].mesh.lons]
        self.las = [self.msrf.surfaces[0].mesh.lats,
                    self.msrf.surfaces[1].mesh.lats]

    def test_get_edge_set(self):

        # The vertexes of the expected edges are the first and last vertexes of
        # the topmost row of the mesh
        expected = [np.array([[-70.33, 19.65, 0.],
                              [-70.57722702, 19.6697801, 0.0]]),
                    np.array([[-70.10327766, 19.67957463, 0.0],
                              [-70.33, 19.65, 0.0]])]

        if PLOTTING:
            _, ax = plt.subplots(1, 1)
            for sfc in self.msrf.surfaces:
                col = np.random.rand(3)
                mesh = sfc.mesh
                ax.plot(mesh.lons, mesh.lats, '.', color=col)
                ax.plot(mesh.lons[0, :],  mesh.lats[0, :], lw=3)
            for edge in self.msrf.edge_set:
                ax.plot(edge[:, 0], edge[:, 1], 'x-r')
            plt.show()

        # Note that method is executed when the object is initialized
        ess = self.msrf.edge_set
        for es, expct in zip(ess, expected):
            np.testing.assert_array_almost_equal(es, expct, decimal=2)

    def test_get_strike(self):
        # Since the two surfaces dip to the north, we expect the strike to
        # point toward W
        msg = 'Multi fault surface: strike is wrong'
        strike = self.msrf.get_strike()
        self.assertAlmostEqual(268.867, strike, places=2, msg=msg)

    def test_get_dip(self):
        dip = self.msrf.get_dip()
        expected = 69.649
        msg = 'Multi fault surface: dip is wrong'
        aae(dip, expected, err_msg=msg, decimal=2)

    def test_get_width(self):
        """ check the width """
        # Measuring the width
        width = self.msrf.get_width()
        np.testing.assert_allclose(width, 20.44854)

    def test_get_area(self):
        # The area is computed by summing the areas of each section.
        a1 = self.msrf.surfaces[0].get_area()
        a2 = self.msrf.surfaces[1].get_area()
        area = self.msrf.get_area()
        aae(a1 + a2, area)

    def test_get_bounding_box(self):
        bb = self.msrf.get_bounding_box()

        if PLOTTING:
            _, ax = plt.subplots(1, 1)
            ax.plot([bb.west, bb.east, bb.east, bb.west],
                    [bb.south, bb.south, bb.north, bb.north], '-')
            ax.plot(self.los[0], self.las[0], '.')
            ax.plot(self.los[1], self.las[1], '.')
            plt.show()

        aae([bb.west, bb.east, bb.south, bb.north],
            [-70.5772, -70.1032, 19.650, 19.7405], decimal=2)

    def test_get_middle_point(self):
        # The computed middle point is the mid point of the first surface
        midp = self.msrf.get_middle_point()
        expected = [-70.453372, 19.695377, 10.2703]
        computed = [midp.longitude, midp.latitude, midp.depth]
        aae(expected, computed, decimal=4)

    def test_get_surface_boundaries01(self):
        # This checks the boundary of the first surface. The result is checked
        # visually
        blo, bla = self.srfc50.get_surface_boundaries()

        # Saving data
        fname = os.path.join(BASE_PATH, 'results', 'results_t01.npz')
        if OVERWRITE:
            np.savez_compressed(fname, blo=blo, bla=bla)

        # Load expected results
        er = np.load(fname)

        if PLOTTING:
            _, ax = plt.subplots(1, 1)
            ax.plot(er['blo'], er['bla'], '-r')
            plt.show()

        # Testing
        aae(er['blo'], blo, decimal=1)
        aae(er['bla'], bla, decimal=1)

    @unittest.skip("skipping due to differences betweeen various architectures")
    def test_get_surface_boundaries(self):
        # The result is checked visually
        blo, bla = self.msrf.get_surface_boundaries()

        # Saving data
        fname = os.path.join(BASE_PATH, 'results', 'results_t02.npz')
        if OVERWRITE:
            np.savez_compressed(fname, blo=blo, bla=bla)

        # Load expected results
        er = np.load(fname)

        if PLOTTING:
            _, ax = plt.subplots(1, 1)
            ax.plot(blo, bla, '-r')
            ax.plot(self.los[0], self.las[0], '.')
            ax.plot(self.los[1], self.las[1], '.')
            plt.show()

        # Testing
        aae(er['blo'], blo, decimal=2)
        aae(er['bla'], bla, decimal=2)

    def test_get_rx(self):
        # Results visually inspected
        dst = self.msrf.get_rx_distance(self.mesh)

        if PLOTTING:
            title = f'{self.NAME} - Rx'
            _plt_results(self.clo, self.cla, dst, self.msrf, title)

    def test_get_ry0(self):
        # Results visually inspected
        dst = self.msrf.get_ry0_distance(self.mesh)

        if PLOTTING:
            title = f'{self.NAME} - Rx'
            _plt_results(self.clo, self.cla, dst, self.msrf, title)


def _plt_results(clo, cla, dst, msrf, title):
    """ Plot results """
    _ = plt.figure()
    ax = plt.gca()
    plt.scatter(clo, cla, c=dst, edgecolors='none', s=15)
    plot_mesh_2d(ax, msrf.surfaces[0])
    plot_mesh_2d(ax, msrf.surfaces[1])
    lo, la = msrf.get_surface_boundaries()
    plt.plot(lo, la, '-r')
    z = np.reshape(dst, clo.shape)
    cs = plt.contour(clo, cla, z, 10, colors='k')
    _ = plt.clabel(cs)
    plt.title(title)
    plt.show()
