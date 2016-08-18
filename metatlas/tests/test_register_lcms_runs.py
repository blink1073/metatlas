from __future__ import print_function
import os

import numpy as np
import tables

from metatlas.mzml_loader import mzml_to_hdf, get_test_data
from metatlas.h5_query import (
    get_chromatogram, get_data, get_spectrogram, get_heatmap,
    get_info)
from metatlas.plotting import (
    plot_heatmap, plot_spectrogram, plot_chromatogram
)


from metatlas.helpers import dill2plots as dp

from metatlas.helpers import metatlas_get_data_helper_fun as ma_data
from metatlas import metatlas_objects as metob
from metatlas.helpers import rt_corrector as rt_corrector
from ipywidgets import interact, interactive, fixed



def test_interact_get_metatlas_files():
    experiment = '%violacein%'
    name = '%_%'
    most_recent = False
    files = dp.get_metatlas_files(experiment=experiment, name=name, most_recent=most_recent)
    assert len(files) == 1350

    experiment = '%violacein%'
    name = '%_%'
    most_recent = False
    files = dp.get_metatlas_files(experiment=experiment, name=name, most_recent=most_recent)
    assert len(files) == 1350

    experiment = '%violacein%'
    name = '%_%'
    most_recent = False
    files = dp.get_metatlas_files(experiment=experiment, name=name, most_recent=most_recent)
    assert len(files) == 1350

    experiment = '%violacein%'
    name = '%_%'
    most_recent = False
    files = dp.get_metatlas_files(experiment=experiment, name=name, most_recent=most_recent)
    assert len(files) == 1350

    experiment = '%violacein%'
    name = '%_%'
    most_recent = False
    files = dp.get_metatlas_files(experiment=experiment, name=name, most_recent=most_recent)
    assert len(files) == 1350

    experiment = '%violacein%'
    name = '%_%'
    most_recent = False
    files = dp.get_metatlas_files(experiment=experiment, name=name, most_recent=most_recent)
    assert len(files) == 1350




def test_make_empty_fileinfo_sheet():
    experiment = '%violacein%'
    name = '%_%'
    most_recent = False
    f = dp.get_metatlas_files(experiment=experiment, name=name, most_recent=most_recent)
    dp.make_empty_fileinfo_sheet('/global/homes/b/bpb/Downloads/empty_violacein_384_finfo.tab', f.files)

    # see if the file exits
