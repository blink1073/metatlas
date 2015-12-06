"""
Module used to define H5 queries.
"""
from __future__ import print_function

import tables
import numpy as np


def get_data(h5file, ms_level, polarity, **kwargs):
    """
    Get raw data from an h5file meeting given criteria.

    Parameters
    ----------
    h5file: string or open pytables file
        The path to the h5file or open file handle.
    ms_level : int
        MS Level.
    polarity : int
        Plus proton (1) or Minus proton (0).
    **kwargs
        Optional search modifiers.  (e.g. min_r=0, max_mz=100, precursor_MZ=1).
        Use verbose=True for displaying query messages.

    Returns
    -------
    out : dictionary
        Dictionary with arrays for 'i', 'mz', and 'rt' values meeting criteria.
    """
    if not isinstance(h5file, tables.File):
        h5file = tables.open_file(h5file)

    if ms_level == 1:
        if not polarity:
            table = h5file.root.ms1_neg
        else:
            table = h5file.root.ms1_pos
    elif not polarity:
        table = h5file.root.ms2_neg
    else:
        table = h5file.root.ms2_pos

    if not table.nrows:
        return None

    query = ''

    for name in ['rt', 'mz', 'precursor_MZ', 'precursor_intensity',
                 'collision_energy']:
        if 'min_%s' % name in kwargs:
            query += ' & (%s >= %s)' % (name, kwargs['min_%s' % name])
        if 'max_%s' % name in kwargs:
            query += ' & (%s <= %s)' % (name, kwargs['max_%s' % name])
        if name in kwargs:
            query += ' & (%s == %s)' % (name, kwargs[name])

    if not query:
        data = table.read()
        return data

    # chop off the initial ' & '
    query = query[3:]
    if kwargs.get('verbose', None):
        print('Querying: %s from %s' % (query, table._v_name))

    data = table.read_where(query)

    if not data.size:
        raise ValueError('No data found matching criteria')

    if kwargs.get('verbose', None):
        print('Query complete')

    return data


def get_chromatogram(h5file, min_mz, max_mz, ms_level, polarity,
                     aggregator=np.sum, **kwargs):
    """
    Get Chromatogram data - RT vs. intensity aggregation

    Parameters
    ----------
    h5file: string or open pytables file
        The path to the h5file or open file handle.
    min_mz : float
        Minimum m/z value.
    max_mz : float
        Maximum m/z value.
    ms_level : int
        MS Level.
    polarity: int
        Plus proton (1) or Minus proton (0).
    aggregator: function
        Function to aggregate the intensity data.  Defaults to np.sum,
        producing an XIC. For Base Peak Chromatogram, use np.max.
    **kwargs
        Optional search modifiers.  (e.g. precursor_MZ=1,
            min_collision_energy=4)

    Returns
    -------
    out : tuple of arrays
        (rt_vals, i_vals) arrays in the desired range.
    """
    data = get_data(h5file, ms_level, polarity, min_mz=min_mz,
                    max_mz=max_mz, **kwargs)
    if data is None:
        return [], []
    rt = np.unique(data['rt'])
    edges = np.argwhere(np.diff(data['rt']) > 0).squeeze()
    start = 0
    i = []
    for e in edges:
        i.append(aggregator(data['i'][start:e]))
        start = e
    i.append(aggregator(data['i'][start:]))
    return rt, np.array(i)


def get_heatmap(h5file, mz_bins, ms_level, polarity, **kwargs):
    """
    Get a HeatMap of RT vs MZ.

    Parameters
    ----------
    h5file: string or open pytables file
        The path to the h5file or open file handle.
    mz_steps : int or array-like
        Bins to use for the mz axis.
    ms_level : int
        MS Level.
    polarity: int
        Plus proton (1) or Minus proton (0).
    **kwargs
        Optional search modifiers.  (e.g. precursor_MZ=1,
            min_collision_energy=4)

    Returns
    -------
    out : dict
        Dictionary containing: 'arr', 'rt_bins', 'mz_bins'.
    """
    data = get_data(h5file, ms_level, polarity, **kwargs)
    if data is None:
        return None

    rt_values = np.unique(data['rt'])
    rt_bins = np.hstack((rt_values, rt_values[-1] + 1))
    arr, mz_bins, _ = np.histogram2d(data['mz'], data['rt'],
                                     weights=data['i'],
                                     bins=(mz_bins, rt_bins))

    mz_centroid = (np.sum(np.multiply(np.sum(arr, axis=1), mz_bins[:-1]))
                   / np.sum(arr))

    return dict(arr=arr, rt_bins=rt_values, mz_bins=mz_bins,
                mz_centroid=mz_centroid)


def get_spectrogram(h5file, min_rt, max_rt, ms_level, polarity,
                    bins=2000, **kwargs):
    """
    Get cumulative I vs MZ in RT Range (spectrogram)

    Parameters
    ----------
    h5file : table file handle
        Handle to an open tables file.
    min_rt : float
        Minimum retention time.
    max_rt : float
        Maximum retention time.
    ms_level : int
        MS Level.
    polarity: int
        Plus proton (1) or Minus proton (0).
    bins : int or array-like
        Desired bins for the histogram.
    **kwargs
        Optional search modifiers.  (e.g. precursor_MZ=1,
            min_collision_energy=4)

    Returns
    -------
    out : tuple of arrays
        (mz_vals, i_vals) arrays in the desired range.
    """
    data = get_data(h5file, ms_level, polarity, min_rt=min_rt,
                    max_rt=max_rt, **kwargs)
    if data is None:
        return [], []

    i, mz = np.histogram(data['mz'], bins=bins, weights=data['i'])
    # center the bins
    mz = (mz[:-1] + mz[1:]) / 2

    return mz, i


def get_info(h5file):
    """Get info about an LCMS HDF file

    Parameters
    ----------
    h5file: string or open pytables file
        The path to the h5file or open file handle.

    Returns
    -------
    out : dict
        Number of rows for all of the tables in the file.
    """
    if not isinstance(h5file, tables.File):
        h5file = tables.open_file(h5file)

    info = dict()
    for table_name in ['ms1_neg', 'ms1_pos', 'ms2_neg', 'ms2_pos']:
        table = h5file.get_node('/%s' % table_name)
        data = dict()
        data['nrows'] = table.nrows
        if not table.nrows:
            info[table_name] = data
            continue
        data['min_mz'] = table.col('mz').min()
        data['max_mz'] = table.col('mz').max()
        data['min_rt'] = table.col('rt').min()
        data['max_rt'] = table.col('rt').max()
        info[table_name] = data

    return info


if __name__ == '__main__':  # pragma: no cover
    import argparse
    import os
    import matplotlib.pyplot as plt

    desc = "Query and plot MZML data from HDF files"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("-x", "--xic", action="store_true",
                        help="Get and plot XIC")
    parser.add_argument("-s", "--spectrogram", action="store_true",
                        help="Get and plot Spectrogram")
    parser.add_argument("--heatmap", action="store_true",
                        help="Get and plot Heatmap")
    parser.add_argument('input_file', help="Input HDF file",
                        action='store')

    args = parser.parse_args()

    fname = args.input_file
    fid = tables.open_file(fname)
    basename = os.path.splitext(fname)[0]

    if args.xic:
        x, y = get_chromatogram(fid, 0, 100000, 1, 0)
        plot_chromatogram(x, y, title=basename)

    if args.spectrogram:
        x, y = get_spectrogram(fid, 1, 5, 1, 0)
        plot_spectrogram(x, y)

    if args.heatmap:
        data = get_heatmap(fid, 1000, 1, 0)
        plot_heatmap(data['arr'], data['rt_bins'], data['mz_bins'])

    plt.show()
