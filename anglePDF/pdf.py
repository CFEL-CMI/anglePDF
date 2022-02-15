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

import git
import os
import h5py
import anglePDF.expsim as expsim
import os


class AnglePDF(object):
    """Define a rudimentary template class to demonstrate documentation and installation"""

    def __init__(self, filename):
        """Initialize object

        param filename Specifies the file to work with, can be new if data is to be written.
        Receive a filename in following format
        name of angular distribution- exp value - sample size
        for e.g. fh95-1D-0.85-10000
        means angle for Friedrich Herschbach angular distribution which has 0.85 experimental value, 1D alignment
        and 10000 molecule
        """
        self._fname = filename
        self.func_name = filename.split('-')[0]
        self.alignment = filename.split('-')[1]
        self.measurement = float(filename.split('-')[2])
        self.sample_size = int(filename.split('-')[3])
        self._data = None
        self.load()

    def load(self):
        """Load data from the current file"""
        try:
            h5py.File(f'pdf_file/{self._fname}.h5')
        except FileNotFoundError:
            print('Sampling...')
            self.sample(self.func_name, self.measurement, self.sample_size)

        if os.path.exists(f'pdf_file/{self._fname}.h5') == False:
            print(f'Either file or distribution does not exists')
        else:
            fn = h5py.File(f'pdf_file/{self._fname}.h5')
            print('The angular distribution has the following details:')
            for key in fn.attrs.keys():
                print(f'{key} -> {fn.attrs[key]}')

    def save(self):
        """Save the provided data to file"""
        # flush file
        repo = git.Repo(search_parent_directories=True)
        commit = repo.head.object.hexsha
        fname = h5py.File(f'pdf_file/{self._fname}.h5', 'w')
        fname.create_dataset(name='phi', data=self._data[0])
        fname.create_dataset(name='theta', data=self._data[1])
        fname.create_dataset(name='chi', data=self._data[2])
        metadata = {'Distribution name': self.func_name,
                    'Alignment': '1D',
                    'Expectation_value': self.measurement,
                    'git commit': commit
                    }
        fname.attrs.update(metadata)
        fname.close()

    def sample(self, dist_name, exp_value, n=1000):
        """Sample the PDF

        param n Provide `n` many randomly sampled directions from the PDF (probability weighted, obviously;-)
        """
        if dist_name == 'fh95':
            sim_data = expsim.FHDist(measurement=exp_value, sample=n)
            self._data = sim_data.sampler()
            self.save()
        else:
            print('The distribution function has not been added yet')
