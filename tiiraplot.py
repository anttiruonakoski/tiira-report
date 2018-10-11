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
from bokeh.embed import file_html

class Chart(object)

    def __init__(self):
        self.data = data
        self.plot = plot
        
    def embedded ():
        script, div = components(self.plot)
        return script, div

    def html():
        return file_html(self.plot, CDN, "Tiira")


class SumChart(Chart)

    def __init__(self):
        self.data = data
        p = []

        source = ColumnDataSource(data)

        high = data[data['Määrä'] > data['Määrä'].quantile(.9)]
        low = data[data['Määrä'] <= data['Määrä'].quantile(.9)]

        sourcehigh = ColumnDataSource(high)
        sourcelow = ColumnDataSource(low)

        lajit = source.data['Laji'].tolist()[::-1]
        title = f'Tiiraan ilmoitettua yksilöä, viimeiset {period} päivää'

        p.append(figure(plot_width = 640, plot_height = 500, x_axis_type='linear',
                title = title,
                y_range=lajit))

        labels = LabelSet(x='Määrä', y='Laji', text='Määrä', level='glyph',x_offset=5, source=sourcelow, text_font_size='8pt', text_baseline='middle')
        labelshigh = LabelSet(x='Määrä', y='Laji', text='Määrä', level='glyph',x_offset=-30, source=sourcehigh, text_font_size='8pt', text_baseline='middle', text_color='#FFFFFF')
        
        #visual
        p[key].x_range.start = 0
        p[key].toolbar.logo = None
        p[key].toolbar_location = None
        p[key].yaxis.major_tick_line_color = None  # turn off y-axis major ticks
        p[key].yaxis.minor_tick_line_color = None
        p[key].xaxis.minor_tick_line_color = None
        p[key].ygrid.grid_line_color = None
        p[key].toolbar.active_drag = None
        p[key].hbar(y='Laji', right='Määrä', left=0, height=0.75, source=source)
        p[key].add_layout(labels)
        p[key].add_layout(labelshigh)




class SubmitterTable(Chart, data)

if __name__ == "__main__":

    # Set to output the plot in the notebook

    filename = 'x.html'
    output_file(filename, title='Bokeh Plot', mode='cdn', root_dir=None)
    save(p)