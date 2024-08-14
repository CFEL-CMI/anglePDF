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
from tqdm import tqdm
from scipy import interpolate
import pkg_resources
import random

class ExpSimPDF(object):
    """Simulate angular PDF from experimental parameters

    Attributes:
    ----------
    alignment : int
        Dimensionality of the alignment i.e. 1D or 3D (default 1)
    measurement : float
        Experimental value of the aligning the molecule (default 2)
    sample : int
        Sample size of the molecular beam (default 1000)
    expectation_values : list
        List of the expectation value of the euler angles

    References:
    # Friedrich, B. & Herschbach, D. Polarization of Molecules Induced by Intense Nonresonant Laser Fields. J Phys Chem 99, 15686–15693 (1995).
    # Friedrich, B. & Herschbach, D. Alignment and Trapping of Molecules in Intense Laser Fields. Phys Rev Lett 74, 4623–4626 (1995).
    # Stapelfeldt, H. & Seideman, T. Colloquium: Aligning molecules with strong laser pulses. Rev Mod Phys 75, 543–557 (2003).  
    """

    def __init__(self, alignment: int, expection_values : list, sample: int, measurement : float = None):
        """
        Parameters:
        ----------
        alignment : int
            dimensionality of alignment i.e. 1D or 3D (default 1)
        measurement : float
            Experimental value of the aligning the molecule (default 2)
        sample : int
            Sample size of the molecular beam (default 1000)
        expectation_values : list
            List of the expectation value of the euler angles

        The sigma values are calculated as follows (1 - <\\cosx>^2) where x can be \\chi, \\theta, \\phi
        """
        self.alignment = alignment
        assert self.alignment == 1 or self.alignment == 3, "The dimension of the alignment is not 1D or 3D"
        if self.alignment == 1:
            self.sampler = self.angle_sampler_1D
        elif self.alignment == 3:
            self.sampler = self.angle_sampler_3D
        self.cos_chi, self.cos_theta, self.cos_phi = expection_values[0], expection_values[1], expection_values[2]
        self.sigma_chi, self.sigma_theta, self._sigma_phi = 1 - self.cos_chi, 1 - self.cos_theta, 1 - self.cos_phi
        
        self.sample = sample
        self.measurement = measurement

    
    @staticmethod
    def fh_func(cost, sigma):
        """
        Parameters
        ----------
        cost : float
            expected value between -1 and 1. calculate the Friedrich Herschbach distribution
        sigma : float
            the width of the Guassian curve

        Returns
        -------
            Distribution value at the given value of \sin\theta and sigma value
        """
        return np.exp(-0.5 * (1 - cost ** 2) / sigma ** 2)

    def fh_func_sin(sint, sigma):
        """
        Same as the fh_func the angle are \\pi/2 shifted
        Parameters
        ----------
        cost : float
            expected value between -1 and 1. calculate the Friedrich Herschbach distribution
        sigma : float
            the width of the Guassian curve

        Returns
        -------
            Distribution value at the given value of \sin\theta and sigma value
        """
        return np.exp(-0.5 * (sint ** 2) / sigma)

    @property
    def angle_sampler_1D(self):
        """
        Returns:
            numpy array of the distribution of theta, phi and chi angles

        The function generates arrays of 'n' (sample number) theta, phi and chi  angles for 1D alignment
        using rejection sampling. The distribution os given by Friedrich Herschbach
        n\\theta = \\exp(-\\frac{\\sin^2\\theta}{2\\sigma^2})
        If the value of sigma is given from 2D data from detector. 
        The value of sigma will be manipulated using calculated 2D and 3D expectation values
        saved in data sub-folder in anglePDF. 
        """
        phi = np.random.uniform(0, 2 * np.pi, self.sample, )
        chi = np.random.uniform(0, 2 * np.pi, self.sample, )
        theta = np.zeros(self.sample,)
        i = 0
        while i < self.sample:
            proposal = np.random.uniform(0, 1)
            proposal = np.random.uniform(-np.pi/2, np.pi/2)
            v = np.random.rand()
            if v <= self.fh_func(np.cos(proposal), self.sigma_theta):
                theta[i] = proposal
                i += 1
        
        p_theta = self.fh_func(np.cos(theta), self.sigma_theta)
        weights = p_theta 
        weights = weights/weights.max()  

        return (chi, theta, phi, weights)

    def expectation_values_from_2D(self):
        "Method calculates the sigma for 3D from 2D values of detector"
        fn = pkg_resources.resource_stream('anglePDF', 'data/cos3d_cos2d_sigma.h5')
        f = h5py.File(fn, 'r')
        cos2theta_2d = np.asarray(f['cos2theta_2d'])
        sigmas = np.asarray(f['sigma'])
        f.close()
        sigma_interp = interpolate.interp1d(cos2theta_2d, sigmas)
        sigma = sigma_interp(self.measurement)

        return sigma
    
    @property
    def angle_sampler_3D(self):
        """The function generates arrays of 'n' (sample number) theta, phi and chi  angles for 1D alignment
        using rejection sampling. The weights of at a given set of euler angle [chi, theta, phi] is calculated by 
        p(\\theta) * p(\\chi) * p(\\phi). The function p comes from n\\theta = \\exp(-\\frac{\\sin^2\\theta}{2\\sigma^2})
        where the sigmas corresponds to the width of the guassian as explained in the references"""
        phi, chi, theta = [], [], []

        pbar = tqdm(total=self.sample, desc="Theta Processing")
        #THETA
        i = 0
        while i < self.sample:
            proposal = np.random.uniform(0, np.pi)
            v = np.random.rand()
            if v <= self.fh_func(np.cos(proposal), self.sigma_theta):
                theta.append(proposal)
                i += 1
                pbar.update(1)

        pbar = tqdm(total=self.sample, desc="Phi Processing")
        # PHI
        i = 0
        while i < self.sample:
            proposal = np.random.uniform(0, np.pi)
            v = np.random.rand()
            if v <= self.fh_func(np.cos(proposal), self.sigma_phi):
                phi.append(proposal)
                i += 1
                pbar.update(1)
            
            
        pbar = tqdm(total=self.sample, desc="Chi Processing")
        # CHI
        i = 0
        while i < self.sample:
            proposal = np.random.uniform(0, np.pi)
            v = np.random.rand()
            if v <= self.fh_func_sin(np.cos(proposal), self.sigma_chi):
                chi.append(proposal)
                #theta[i] = np.arccos(proposal)
                i += 1
                pbar.update(1)

        p_phi = self.fh_func(np.cos(phi), self.sigma_phi)
        p_theta = self.fh_func(np.cos(theta), self.sigma_theta)
        p_chi = self.fh_func_sin(np.cos(chi), self.sigma_chi)

        weights = p_chi * p_theta * p_phi

        #Normalising the weights
        weights = weights/weights.max()  

        return (chi, theta, phi, weights)


class AnatSimPDF():
    """
    This class would calculate the angle distribution using Sebastian's analytical formula. For this you 
    will require the polarizability tensor, Laser intensity (elliptical). Further this works similar to the 
    class ExpSimPDF"""
    def __init__(self):
        pass
        

