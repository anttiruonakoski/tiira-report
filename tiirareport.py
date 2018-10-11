#!/usr/bin/env python3

"""tiirareport.py: Generate Jinja2 template based HTML-document from Bokeh sub-components."""

__author__ = "Antti Ruonakoski"
__copyright__ = "Copyright 2018"
__credits__ = ["Antti Ruonakoski"]
__license__ = "MIT"
__version__ = ""
__maintainer__ = "Antti Ruonakoski"
__email__ = "aruonakoski@gmail.com"
__status__ = "Development"

template_file_name = 'base.html'

from jinja2 import Environment, FileSystemLoader
import numpy as np
import pandas as pd
import argparse, sys

from bokeh.plotting import figure
from bokeh.io import show, output_file, save
from bokeh.models import ColumnDataSource, LabelSet
from bokeh.layouts import column
from bokeh.resources import CDN
from bokeh.embed import file_html

from tiiradataframe import *
from tiiraplot import *

class Report(object):

    def __init__(self, figures, tables):          
        self.figures = figures
        self.tables = tables
        self.data = dict(figures=figures, tables=tables)
        
    def compose(self):    
        file_loader = FileSystemLoader('templates')
        env = Environment(loader=file_loader)  
        template = env.get_template(template_file_name)
        output = template.render(data=self.data)
        return output

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Generate a datetime limited pandas.py dataframe")
    #parser.add_argument("-d", "--days", type=int, help="show days past (default 7)", default=7)
    parser.add_argument("-f", "--filename", type=str, help="downloaded file name (default tiira.csv)", default="tiira.csv")
    args = parser.parse_args()
    #main(days_past=args.days, csv_filename=args.filename)
    try:
        df = read_csv(args.filename)
    except IOError as e:
        print(f'virhe tiedoston {args.filename} avaamisessa', e)
        sys.exit(1)

    plotdata = {}
    figures, tables = [], []

    #ACTUAL PLOTTING    
    #sort keys yksilosumma, havaintorivisumma
    #
    columns = {
        'havainnot': ['havaintorivisumma', 'Tiiraan ilmotettua havaintoriviä, viimeiset '],
        'yksilot':  ['yksilosumma', 'Tiiraan ilmotettua yksilöä, viimeiset ']
    }
    for days in [7, 30]:
        for key, value in columns.items():    
            print(key, value[0])
            plotkey = str(days) + key   
            x = df.pipe(filter_submit_period, days=days) \
                                        .pipe(groupbylaji) \
                                        .pipe(sort, sortkey=value[0]).head(15) 
            #drop all columns but laji and aggregate                            
            plotdata[plotkey] = x[['laji', value[0]]]
            title = value[1] + str(days) + ' päivää'

            s,d = (SumChart(data = plotdata[plotkey], title = title).embedded())
            figures.append(dict(script=s,div=d))

        plotdata[str(days) + 'tallentajat'] = df.pipe(filter_submit_period, days=days) \
                                .pipe(groupbysubmitter) \
                                .pipe(sort, sortkey='havaintoa').head(5)

        title = 'Ahkerimmat havaintojen tallentajat, viimeiset ' + str(days) + ' päivää'
        d = pd.DataFrame.to_html(plotdata[str(days) + 'tallentajat'], index=False)
        #s,d = (TableChart(data = plotdata[str(days) + 'tallentajat'], title = title).embedded())
        tables.append(d)                    

    # print (plotdata['30havainnot']) 
    # d = plotdata['30havainnot'].describe(include='all')                             
    # print (d)                              

    report = Report(figures, tables).compose()

    with open ('reports/report.html', 'w') as r:
       r.write(report)

# <3 pandas & bokeh      

