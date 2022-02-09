#!/usr/bin/env python
# -*- coding: utf-8; fill-column: 120 -*-
#
# Copyright (C) 2021 Jochen Küpper <jochen.kuepper@cfel.de>
#
# This file is part of CMI anglePDF
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# If you use this program for scientific work, you must correctly reference it; see LICENSE file
# for details.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program. If not,
# see <http://www.gnu.org/licenses/>.
import numpy as np
import h5py
import pkgutil


class FHDist(object):
    def __init__(self, measurement, alignment, sample):
        """
        Caluculate the theta and phi angle array coressponding to the angular distribution given Friedrich and Herschabch
        paper DOI :  https://doi.org/10.1103/PhysRevLett.74.4623

        Param: cos2theta_2D value, alignment and number of molecules in sample

        Method : The sigma that is the variance of the Guassian distribution. Sigma can be determined by looking into
        pre-calculated values using the monte carlo integration. The pre-calculated value ore stored in the data file.
        The code for the pre-calculation can be looked in the package.
        """
        self.measurement = measurement
        self.alignment = alignment
        self.sample = sample
        # the expectation value of $\cos^2\theta_2D$ should be between 0.5 and 1
        if measurement < 1/2 or measurement > 1:
            raise Exception("The expectation value is not valid")
        if alignment == 3:
            self.angle_sampler_3d()
        else:
            self.angle_sampler_1d(self.measurement, self.sample)

    def fh_func(self, cost, sigma):
        return np.exp(-0.5*(1-cost**2)/sigma**2)

    def angle_sampler_3d(self):
        pass

    def angle_sampler_1d(self, exp_value, n):
        """the function generates arrays of 'n' (sample number) theta nad phi angles using rejection sampling

        param: the experimnetal value of $\cos^2\theta_2D$ and sample size
        In case of 1D alignment the \phi (azimuthal angle) will hae a unifrom distribution between 0 to 2\pi. The
        \theta (inclination) that is the angle with respect to the z-axis shall follow a Guassian distribution
        given by Friedrich and Herschbach
        """
        phi = np.random.uniform(0, 2*np.pi, n)
        thetas = np.zeros(n)
        i = 0
        while i < n:
            proposal = np.random.uniform(-1, 1)
            v = np.random.rand()
            if v <= self.fh_func(proposal, sigma):
                thetas[i] = np.arccos(proposal)
                i += 1
