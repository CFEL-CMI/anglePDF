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
from scipy import interpolate
import matplotlib.pyplot as plt


class ExpSimPDF(object):
    """Simulate angular PDF from experimental parameters"""

    def __init__(self, alignment=1, measurement=2, data=(0.5,), sample=1000):
        """Initialize object

        param alignment Specify the dimensionality of the alignment, i.e., 1D or 3D

        param measurement Specify the projection-dimensionality of the degrees of alignment, i.e., $\cos^2\theta_{2D}$
        or $\cos^2\theta_{3D}$

        param data

        """
        self.alignment = alignment
        self.measurement = measurement
        self.sample = sample

        # open file
        self._pdf = []

    def pdf(self, file):
        """Load data from the current file"""
        return self._pdf


class FHDist(ExpSimPDF):
    def __init__(self, alignment=1, measurement=0.5, data=(0.5,), sample=1000):
        """
        Calculate the theta and phi angle array corresponding to the angular distribution given Friedrich and
        Herschbach paper DOI :  https://doi.org/10.1103/PhysRevLett.74.4623

        Param: cos2theta_2D value, alignment and number of molecules in sample

        Method : The sigma that is the variance of the Guassian distribution. Sigma can be determined by looking into
        pre-calculated values using the monte carlo integration. The pre-calculated value ore stored in the data file.
        The code for the pre-calculation can be looked in the package.
        """
        super().__init__(alignment, measurement, data, sample)
        # the expectation value of $\cos^2\theta_2D$ should be between 0.5 and 1
        if self.measurement < 1 / 2 or self.measurement > 1:
            raise Exception("The expectation value is not valid")

    @staticmethod
    def fh_func(cost, sigma):
        return np.exp(-0.5 * (1 - cost ** 2) / sigma ** 2)

    def sampler(self):
        if self.alignment == 3:
            self.angle_sampler_3d()
        else:
            self.angle_sampler_1d()

    def angle_sampler_3d(self):
        return
        pass

    def angle_sampler_1d(self):
        """the function generates arrays of 'n' (sample number) theta nad phi angles using rejection sampling

        param: the experimental value of $ \cos^2 \theta_2D $ and sample size
        In case of 1D alignment the \phi (azimuthal angle) will have a uniform distribution between 0 and 2\pi. The
        \theta (inclination) that is the angle with respect to the z-axis shall follow a Guassian distribution
        given by Friedrich and Herschbach
        """
        print('@angle_sampler_1d')
        phi = np.random.uniform(0, 2 * np.pi, self.sample)
        chi = np.random.uniform(0, 2 * np.pi, self.sample)
        theta = np.zeros(self.sample)
        f = h5py.File('data/cos3d_cos2d_sigma.h5', 'r')
        cos2theta_2d = np.asarray(f['cos2theta_2d'])
        sigmas = np.asarray(f['sigma'])
        f.close()
        sigma_interp = interpolate.interp1d(cos2theta_2d, sigmas)
        sigma = sigma_interp(self.measurement)
        i = 0
        while i < self.sample:
            proposal = np.random.uniform(-1, 1)
            v = np.random.rand()
            if v <= self.fh_func(proposal, sigma):
                theta[i] = np.arccos(proposal)
                i += 1
        print(phi, theta, chi ,'\n', sigma)
        plt.hist(theta, bins=100)
        plt.show()
        return np.array([phi, theta, chi])
