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

#import git
import h5py

class AnglePDF(object):
    """Define a rudimentary template class to demonstrate documentation and installation"""

    def __init__(self, filename):
        """Initialize object

        param filename Specifies the file to work with, can be new if data is to be written.
        """
        self.func_name = filename.split('-')[0]
        self.measurement = filename.split('-')[1]
        self.sample_size = filename.split('-')[2]
        try:
            h5py.File(f'pdf_file/{filename}.h5', 'r')
            self.load(filename)
        except:
            print('Currently no file exits with the given values \nWorking on creating probability density function...')
            self.sample(self.func_name,self.measurement,self.sample_size)


    def load(self, file):
        """Load data from the current file"""
        self._data = []


    def save(self, data):
        """Save the provided data to file"""
        self._data = data
        #flush file


    def sample(self, n=1000):
        """Sample the PDF

        param n Provide `n` many randomly sampled directions from the PDF (probability weighted, obviously;-)
        """

