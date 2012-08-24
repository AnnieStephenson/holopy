# Copyright 2011, Vinothan N. Manoharan, Thomas G. Dimiduk, Rebecca
# W. Perry, Jerome Fung, and Ryan McGorty
#
# This file is part of Holopy.
#
# Holopy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Holopy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Holopy.  If not, see <http://www.gnu.org/licenses/>.
'''
The tests here test basic reconstruction capability

.. moduleauthor:: Rebecca W. Perry <rperry@seas.harvard.edu>
'''
from __future__ import division

import numpy as np
import scipy
from ...core.tests.common import get_example_data
from ..propagate import propagate
from numpy.testing import assert_array_equal
from nose.plugins.attrib import attr


@attr('fast')
def test_reconNear():
    im = get_example_data('image0003.npy', 'optical_train3.yaml')
    gold = get_example_data('recon_4.npy', 'optical_train3.yaml')
    rec_im = propagate(im, 4e-6)
    rec_im = abs(rec_im * scipy.conj(rec_im))
    rec_im = np.around((rec_im-rec_im.min())/(rec_im-rec_im.min()).max()*255)
    assert_array_equal(rec_im.astype('uint8'),gold)

@attr('fast')
def test_reconMiddle():
    gold = get_example_data('recon_7.npy', 'optical_train3.yaml')
    im = get_example_data('image0003.npy', 'optical_train3.yaml')
    rec_im = propagate(im, 7e-6)
    rec_im = abs(rec_im * scipy.conj(rec_im))
    rec_im = np.around((rec_im-rec_im.min())/(rec_im-rec_im.min()).max()*255)
    assert_array_equal(rec_im.astype('uint8'),gold)
    
@attr('fast')
def test_reconFar():
    gold = get_example_data('recon_10.npy', 'optical_train3.yaml')
    im = get_example_data('image0003.npy', 'optical_train3.yaml')
    rec_im = propagate(im, 10e-6)
    rec_im = abs(rec_im * scipy.conj(rec_im))
    rec_im = np.around((rec_im-rec_im.min())/(rec_im-rec_im.min()).max()*255)
    assert_array_equal(rec_im.astype('uint8'),gold)
