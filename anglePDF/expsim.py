#!/usr/bin/env python3
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
import pkg_resources


class ExpSimPDF(object):
    """Simulate angular PDF from experimental parameters

    Attributes
    ----------
    alignment : int
        Dimensionality of the alignment i.e. 1D or 3D (default 1)
    measurement : float
        Experimental value of the aligning the molecule (default 2)
    sample : int
        Sample size of the molecular beam (default 1000)
    """

    def __init__(self, alignment: int = 1, measurement: float = 2, data=(0.5,), sample: int = 1000):
        """
        Parameters
        ----------
        alignment : int
            dimensionality of alignment i.e. 1D or 3D (default 1)
        measurement : float
            Experimental value of the aligning the molecule (default 2)
        sample : int
            Sample size of the molecular beam (default 1000)
        """
        self.alignment = alignment
        self.measurement = measurement
        self.sample = sample

        # open file
        self._pdf = []

    # def pdf(self, file):
    #    """Load data from the current file"""
    #    return self._pdf


class FHDist(ExpSimPDF):
    """
    Subclass of ExpSimPDF
    Simulate angular PDF from experimental values of aligning molecular beam using strong linearly polarised LASER

    Attributes
    ----------
    alignment : int
        Dimensionality of the alignment i.e. 1D or 3D (default 1)
    measurement : float
        Experimental value of the aligning the molecule (default 0.5)
    sample : int
        Sample size of the molecular beam (default 1000)

    Methods
    -------
    sampler()
        Samples angular distribution according to Friedrich Herschbach Guassian plot
        DOI :  https://doi.org/10.1103/PhysRevLett.74.4623

    fh_func()
        static function returning Friedrich and Herschbach angular distribution function
    """
    def __init__(self, alignment=1, measurement=0.5, data=(0.5,), sample=1000):
        """
        Parameters
        ----------
        alignment : int
            Dimensionality of the alignment i.e. 1D or 3D (default 1)
        measurement : float
            Experimental value of the aligning the molecule (default 0.5)
        sample : int
            Sample size of the molecular beam (default 1000)

        Raises
        ------
        Raises exception if experimental value of degree of alignment is <0.5 or >1

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
        """
        Parameters
        ----------
        cost : float
            expected value between -1 and 1. calculate the Friedrich Herschbach distribution
        sigma : float
            the width of the Guassian curve

        Return
        ------
        Distribution value at the given value of \sin\theta and sigma value
        """
        return np.exp(-0.5 * (1 - cost ** 2) / sigma ** 2)

    def sampler(self):
        """
        Samples angular distribution according to Friedrich Herschbach with given sample size for either 1D or 3D
        """
        if self.alignment == 3:
            return self.angle_sampler_3d
        else:
            return self.angle_sampler_1d

    @property
    def angle_sampler_3d(self):
        return
        pass

    @property
    def angle_sampler_1d(self):
        """
        The function generates arrays of 'n' (sample number) theta, phi and chi  angles for 1D alignment
        using rejection sampling. The value of sigma is manipulated using calculated 2D and 3D expectation values
        saved in data sub-folder in anglePDF. The distribution os given by Friedrich Herschbach
        r'n\theta = \exp(-\frac{sin^2\theta}{2\sigma^2})'
        """
        phi = np.random.uniform(0, 2 * np.pi, self.sample)
        chi = np.random.uniform(0, 2 * np.pi, self.sample)
        theta = np.zeros(self.sample)
        fn = pkg_resources.resource_stream('anglePDF', 'data/cos3d_cos2d_sigma.h5')
        f = h5py.File(fn, 'r')
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

        return np.array([phi, theta, chi])
