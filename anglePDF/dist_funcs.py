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
import pkgutils


class FHDist(object):
    def __init__(self, measurement, alignment, sample):
        """

        """
        self.measurement = measurement
        self.alignment = alignment
        self.sample = sample
        if measurement < 1/2 or measurement > 1:
            """
            The cos^2theta value for alignment value projection onto a 2D plane lier between 1 and 0.5 
            """
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
        phi = np.random.uniform(0, 2*np.pi, n)
        thetas = np.zeros(n)
        i = 0
        while i < n:
            proposal = np.random.uniform(-1, 1)
            v = np.random.rand()
            if v <= self.fh_func(proposal, sigma):
                thetas[i] = np.arccos(proposal)
                i += 1
