# Copyright 2011-2016, Vinothan N. Manoharan, Thomas G. Dimiduk,
# Rebecca W. Perry, Jerome Fung, Ryan McGorty, Anna Wang, Solomon Barkley
#
# This file is part of HoloPy.
#
# HoloPy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# HoloPy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with HoloPy.  If not, see <http://www.gnu.org/licenses/>.
"""
Misc utility functions to make coding more convenient

.. moduleauthor:: Thomas G. Dimiduk <tdimiduk@physics.harvard.edu>
"""


import os
import shutil
import errno
import numpy as np
import xarray as xr
from copy import copy
import itertools

def _ensure_array(x):
    if np.isscalar(x):
        return np.array([x])
    else:
        return np.array(x)

def ensure_listlike(x):
    if x is None:
        return []
    try:
        iter(x)
        return x
    except TypeError:
        return [x]

def _ensure_pair(x):
    if x is None:
        return None
    try:
        x[1]
        return np.array(x)
    except (IndexError, TypeError):
        return np.array([x, x])

def ensure_3d(x):
    """
    Make sure you have a 3d coordinate.

    If given a 2d coordinate, add a z=0 to make it 3d

    Parameters
    ----------
    x : list, array or tuple with 2 or 3 elements
        a the coordinate that should be 3d

    Returns
    -------
    x3d : np.ndarray
        A coordinate that has 3 elements
    """
    if len(x) not in [2, 3]:
        raise Exception("{0} cannot be interpreted as a coordinate")
    if len(x) == 2:
        return np.append(x, 0)
    else:
        return np.array(x)

def mkdir_p(path):
    '''
    Equivalent to mkdir -p at the shell, this function makes a
    directory and its parents as needed, silently doing nothing if it
    exists.
    '''
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            pass
        else: raise # pragma: no cover

def coord_grid(bounds, spacing=None):
    """
    Return a nd grid of coordinates

    Parameters
    ----------
    bounds : tuple of tuples or ndarray
        Upper and lower bounds of the region
    spacing : float or complex (optional)
        Spacing between points, or if complex, number of points along each
        dimension. If spacing is not provided, then bounds should be integers,
        and coord_grid will return integer indexs in that range
    """
    bounds = np.array(bounds)
    if bounds.ndim == 1:
        bounds = np.vstack((np.zeros(3), bounds)).T

    if spacing:
        if np.isscalar(spacing) or len(spacing) == 1:
            spacing = np.ones(3) * spacing
    else:
        spacing = [None, None, None]

    grid = np.mgrid[[slice(b[0], b[1], s) for b, s in
                     zip(bounds, spacing)]]
    return np.concatenate([g[...,np.newaxis] for g in grid], 3)

def dict_without(d, keys):
    """
    Exclude a list of keys from a dictionary

    Silently ignores any key in keys that is not in the dict (this is
    intended to be used to make sure a dict does not contain specific
    keys)

    Parameters
    ----------
    d : dict
        The dictionary to operate on
    keys : list(string)
        The keys to exclude
    returns : d2
        A copy of dict without any of the specified keys

    """
    d = copy(d)
    for key in _ensure_array(keys):
        try:
            del d[key]
        except KeyError:
            pass
    return d

def is_none(o):
    """
    Check if something is None.

    This can't be done with a simple is check anymore because numpy decided that
    array is None should do an element wise comparison.

    Parameters
    ----------
    o : object
        Anything you want to see if is None
    """

    return isinstance(o, type(None))

def updated(d, update={}, filter_none=True, **kwargs):
    """Return a dictionary updated with keys from update

    Analgous to sorted, this is an equivalent of d.update as a
    non-modifying free function

    Parameters
    ----------
    d : dict
        The dict to update
    update : dict
        The dict to take updates from

    """
    d = copy(d)
    for key, val in itertools.chain(update.items(), kwargs.items()):
        if val is not None:
            d[key] = val

    return d


def squeeze(arr):
    from ..marray import arr_like
    """
    Turns an NxMx1 array into an NxM array.
    """
    keep = [i for i, dim in enumerate(arr.shape) if dim != 1]
    if not hasattr(arr,'spacing') or type(arr.spacing) == type(None):
        spacing = None
    else:
        spacing = np.take(arr.spacing, keep)
    return arr_like(np.squeeze(arr), arr,
                    spacing = spacing)


def arr_like(arr, template=None, **override):
    """
    Make a new Marray with metadata like an old one

    Parameters
    ----------
    arr : numpy.ndarray
        Array data to add metadata to
    template : :class:`.Schema` (optional)
        Marray to copy metadata from. If not given, will be copied from arr
        (probably used in this case for overrides)
    **override : kwargs
        Optional additional keyword args. They will be used to override
        specific metadata

    Returns
    -------
    res : :class:`.Marray`
        Marray like template containing data from arr
    """
    if template is None:
        template = arr

    if not hasattr(template, '_dict'):
        return arr
    meta = template._dict
    meta.update(override)
    return template.__class__(arr, **meta)

def copy_metadata(old, new, do_coords=True):
    def find_and_rename(oldkey, oldval):
        for newkey, newval in new.coords.items():
            if np.array_equal(oldval.values, newval.values):
                return new.rename({newkey: oldkey})
            raise ValueError("Coordinate {} does not appear to have a coresponding coordinate in {}".format(oldkey, new))

    if hasattr(old, 'attrs') and hasattr(old, 'name') and hasattr(old, 'coords'):
        new.attrs = old.attrs
        new.name = old.name
        if hasattr(old, 'z') and not hasattr(new, 'z'):
            new.coords['z'] = old.coords['z']
        if do_coords:
            for key, val in old.coords.items():
                if key not in new.coords:
                    new = find_and_rename(key, val)
    return new

def get_values(a):
    return getattr(a, 'values', a)

def flat(a):
    if hasattr(a, 'flat'):
        return a
    return a.stack(flat=a.dims)

def from_flat(a):
    if hasattr(a, 'flat'):
        return a.unstack('flat')
    return a

def make_subset_data(data, random_subset, return_selection=False):
    if random_subset is None:
        return data
    n_sel = int(np.ceil(data.size*random_subset))
    selection = np.random.choice(data.size, n_sel, replace=False)
    subset = flat(data)[selection]
    subset = copy_metadata(data, subset, do_coords=False)
    if return_selection:
        return subset, selection
    else:
        return subset
