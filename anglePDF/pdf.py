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

import anglePDF
import h5py
import anglePDF.expsim as expsim
import os


class AnglePDF(object):
    """A class for loading, saving and sampling angular distribution.
    ...

    Attributes
    ---------
    fname :  str
        the name of the PDF file in following format (func_name - alignemnt - degree of alignment - sample)
        The parameters are separated by hyphens.
    path : str
        path of the directory to access the angular distribution file (default current working directory)

    Methods
    -------
    load()
        loads the angular distribution file form the given path location
    save()
        saves the sampled angular distribution function into the given path file
    sample()
        samples an angular distribution by calling object class ExpSimPDF
    """

    def __init__(self, fname=None, path=None):
        """
        Parameters
        ----------
        fname : str
            the name of the PDF file in following format (func_name - alignment - degree of alignment - sample)
            The parameters are separated by hyphens.
        path : str
            path of the directory to access the angular distribution file (default current working directory)

        Example
        -------
        fh95-1D-0.85-10000
        means angle for Friedrich Herschbach angular distribution which has, 1D alignment, 0.85 experimental value
        and 10000 molecule
        """
        self._fname = fname
        # variables derived from fname
        self.func_name = fname.split('-')[0]
        self.alignment = fname.split('-')[1]
        self.measurement = float(fname.split('-')[2])
        self.sample_size = int(fname.split('-')[3])
        self._data = None
        if path == None:
            path = os.getcwd()
            self._path = os.path.join(path, f'{self._fname}.h5')
        else:
            self._path = os.path.join(path, f'{self._fname}.h5')

    def load(self):
        """Load data from the current file

        Raises
        ------
        If the angular distribution file of HDF5 format doesn't exist raise the FileNotFound Error
        """
        try:
            h5py.File(self._path)
            fn = h5py.File(self._path, 'r')
            print('The angular distribution has the following details:')
            for key in fn.attrs.keys():
                print(f'{key} -> {fn.attrs[key]}')
            fn.close()
        except FileNotFoundError:
            print("File not found")

    def save(self):
        """Save the provided data to file
        """
        # flush file
        version = anglePDF.__version__
        fname = h5py.File(self._path, 'w')
        fname.create_dataset(name='phi', data=self._data[0])
        fname.create_dataset(name='theta', data=self._data[1])
        fname.create_dataset(name='chi', data=self._data[2])
        metadata = {'Distribution name': self.func_name,
                    'Alignment': '1D',
                    'Expectation_value': self.measurement,
                    'Version': version
                    }
        fname.attrs.update(metadata)
        fname.close()

    def sample(self):
        """Sample the PDF

        param n Provide `n` many randomly sampled directions from the PDF (probability weighted, obviously;-)
        """
        if self.func_name == 'fh95':
            sim_data = expsim.FHDist(measurement=self.measurement, sample=self.sample_size)
            self._data = sim_data.sampler()
            self.save()
        else:
            raise FileNotFoundError('The distribution function has not been added yet')
