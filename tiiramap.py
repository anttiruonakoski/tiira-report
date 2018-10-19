#!/usr/bin/env python3

"""tiiramap.py: plot map from geopandas dataframe."""

__author__ = "Antti Ruonakoski"
__copyright__ = "Copyright 2018"
__credits__ = ["Antti Ruonakoski"]
__license__ = "MIT"
__version__ = ""
__maintainer__ = "Antti Ruonakoski"
__email__ = "aruonakoski@gmail.com"
__status__ = "Development"

import matplotlib
matplotlib.use('Agg')  # non X display backend
import matplotlib.pyplot as plt
from rasterio.plot import show
import rasterio


class Map(object):

    def __init__(self):
        pass

    @staticmethod
    def plot(gdf, mapfilename):

        fig, ax = plt.subplots(figsize=(8, 8), dpi=72.0)

        basemap = 'static/basemap/lly-tumma-base.tif'
        with rasterio.open(basemap, 'r') as src:
            array = src.read()
        plt.axis('off')
        ax.axes.get_xaxis().set_visible(False)
        ax.axes.get_yaxis().set_visible(False)

        show(array, interpolation='sinc', transform=src.transform, ax=ax)

        gdf.plot(marker='+', color='yellowgreen', markersize=12, alpha=0.4, ax=ax)
        try:
            # dpi different in file and display backends, use display dpi. also some unclear variation of raster img ax size compared with jupyter notebook, which produces 9 px shorter image.
            plt.savefig(mapfilename, bbox_inches='tight', pad_inches=0, dpi=72.0)
        except IOError as e:
            print(e)
        return
