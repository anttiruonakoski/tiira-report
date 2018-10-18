#!/usr/bin/env python3

"""tiiraplot.py: create Bokeh plot from pandas DataFrame."""

__author__ = "Antti Ruonakoski"
__copyright__ = "Copyright 2018"
__credits__ = ["Antti Ruonakoski"]
__license__ = "MIT"
__version__ = ""
__maintainer__ = "Antti Ruonakoski"
__email__ = "aruonakoski@gmail.com"
__status__ = "Development"


from bokeh.plotting import figure
from bokeh.io import show, output_file, save
from bokeh.models import ColumnDataSource, LabelSet
from bokeh.layouts import column
from bokeh.resources import CDN
from bokeh.embed import file_html, components
from bokeh.transform import linear_cmap
import colorcet as cc

class Chart(object):

    def __init__(self):
        pass
        
    def embedded (self):
        script, div = components(self.plot)
        return script, div

    def html(self):
        # Set to output the plot in the notebook 
        filename = 'tmp/x.html'
        output_file(filename, title='Bokeh Plot', mode='cdn', root_dir=None)
        save(self.plot)

class SumChart(Chart):

    def __init__(self, data, title):
        self.data = data
        self.title = title
        self.plot = self.make()

    def make(self): 

        data = self.data
        title = self.title

        X = list(data)[1] # X-axle data
        Y = list(data)[0] # Y-axle data

        #print(data) 
        source = ColumnDataSource(data)

        high = data[data[X] > data[X].quantile(.9)]
        low = data[data[X] <= data[X].quantile(.9)]
        max = data[X].max()
        x_offset = -len(str(int(max)))*7.5

        sourcehigh = ColumnDataSource(high)
        sourcelow = ColumnDataSource(low)

        mapper = linear_cmap(field_name=X, palette=cc.blues, low=0 , high=max*0.9)

        lajit = source.data['laji'].tolist()[::-1]

        p = figure(plot_width = 640, plot_height = 400, x_axis_type='linear', title = title, y_range=lajit)

        labels = LabelSet(x=X, y='laji', text=X, level='glyph',x_offset=4, source=sourcelow, text_font_size='8pt', text_baseline='middle')
        labelshigh = LabelSet(x=X, y='laji', text=X, level='glyph', x_offset=x_offset, source=sourcehigh, text_font_size='8pt', text_baseline='middle', text_color='#FFFFFF')
        
        #visual
        p.x_range.start = 0
        p.toolbar.logo = None
        p.toolbar_location = None
        p.yaxis.major_tick_line_color = None  # turn off y-axis major ticks
        p.yaxis.minor_tick_line_color = None
        p.xaxis.minor_tick_line_color = None
        p.ygrid.grid_line_color = None
        p.toolbar.active_drag = None
        p.hbar(y='laji', right=X, left=0, height=0.75, source=source, color=mapper)
        p.add_layout(labels)
        p.add_layout(labelshigh)

        return p

class SubmitterTable(Chart):

    def __init__(self, data, title):
        self.data = data
        self.title = title
        self.plot = self.make()
        pass

if __name__ == "__main__":
    pass

    
    