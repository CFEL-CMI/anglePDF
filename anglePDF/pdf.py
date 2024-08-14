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
import matplotlib.pyplot as plt
import h5py
import os
import anglePDF.expsim as expsim
import numpy as np

import anglePDF.expsim


class AnglePDF():
    """A class for loading, saving and sampling angular distribution.
    ...

    Attributes:
    -----------
    fname :  str
        the name of the PDF file in following format (func_name - alignemnt - degree of alignment - sample)
        The parameters are separated by hyphens.
    path : str
        path of the directory to access the angular distribution file (default current working directory)

    Methods:
    --------
    load()
        loads the angular distribution file form the given path location
    save()
        saves the sampled angular distribution function into the given path file
    sample()
        samples an angular distribution by calling object class ExpSimPDF
    """

    def __init__(self, dist_func):
        """
        Parameters
        ----------
        dimension : int 
            dimension of the alignment distribution. It can only have value 1 corresponding to 1D  and 3 corresponding to 33
        expection_values : list
            List of the expection value of euler angles \\chi, \\theta and \\phi in the same order. Default value is the values for isotropic 
            ensemble
        sample : int
            Number of angle for each euler angle i.e \\chi, \\theta, \\phi
        
        The distribution of the angles is based on the 

        Stapelfeldt, H. & Seideman, T. Colloquium: Aligning molecules with strong laser pulses. Rev Mod Phys 75, 543–557 (2003)
  
        """
        assert dist_func == anglePDF.expsim.ExpSimPDF or anglePDF.expsim.ExpSimPDF, "The angular distribution function has not been implemented yet"
        self.angular_dist_func = dist_func
        self._fname = f"FH95_{self.angular_dist_func.sample}_chi_{self.angular_dist_func.cos_chi:.3f}_
        \\ theta_{self.angular_dist_func.cos_theta:.3f}_phi_{self.angular_dist_func.cos_phi:.3f}.txt".replace(".", "_")

        # variables derived from fname
        path = os.getcwd()
        self._path = os.path.join(path, f'{self._fname}.h5')
        

    def load(self):
        """Load data from the given filename

        Raises:
        ------
        If the angular distribution file of HDF5 format doesn't exist raise the FileNotFound Error
        """
        try:
            h5py.File(self._path)
            fn = h5py.File(self._path, 'r')
            self._data = (fn['chi'], fn['theta'], fn['phi'], fn['weights'])
            print('The angular distribution has the following details:')
            for key in fn.attrs.keys():
                print(f'{key} -> {fn.attrs[key]}')
            fn.close()

        except FileNotFoundError:
            print("File not found")

    def save(self):
        """
        Save the provided data in hdf5 format in given path or cwd otherwise
        """
        # flush file
        version = anglePDF.__version__
        print(self._path)
        fname = h5py.File(self._path, 'w')
        dataset = ['chi', 'theta', 'phi', 'weights']
        for index, angle in enumerate(dataset):
            fname.create_dataset(name=index, data=self._data[index])

        metadata = {'Distribution name': self.angular_dist_func.__class__.__name__,
                    'Alignment': self.angular_dist_func.alignment,
                    'Sample' : self.angular_dist_func.sample
                    'Expectation_value': [self.angular_dist_func.sigma_chi, self.angular_dist_func.sigma_theta, self.angular_dist_func.sigma_phi],
                    'Version': version,
                    }
        fname.attrs.update(metadata)
        fname.close()

    def sample(self):
        """Sample the PDF

        Provides an angular distribution randomly sampled form PDF.

        param n Provide `n` many randomly sampled directions from the PDF (probability weighted, obviously;-)
        """
        self._data = self.angular_dist_func.sampler()

    
    def plot(self):
        # Create a 3D scatter plot
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        sc = ax.scatter(self._data[2], self._data[1], self._data[0], c=self._data[3], cmap='viridis')
        plt.colorbar(sc)
        # Set labels and title
        ax.set_xlabel('phi')
        ax.set_ylabel('theta')
        ax.set_zlabel('chi')
        ax.set_title('3D Grid of Angles')
        plt.show()  
