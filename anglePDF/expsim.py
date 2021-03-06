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
# If you use this programm for scientific work, you must correctly reference it; see LICENSE file
# for details.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program. If not,
# see <http://www.gnu.org/licenses/>.



class ExpSimPDF(object):
    """Simulate anguar PDF from experimental paramters"""

    def __init__(self, alignment=1, measurement=2, data=(0.5,)):
        """Initialize object

        param alignment Specify the dimensionality of the alignment, i.e., 1D or 3D

        param measurement Specify the projection-dimensionality of the degrees of alignment, i.e., $\cos^2\theta_{2D}$
        or $\cos^2\theta_{3D}$

        param data

        """
        # open file
        self._pdf = []
        return self._pdf


    def pdf(self, file):
        """Load data from the current file"""
        refturn self._pdf
