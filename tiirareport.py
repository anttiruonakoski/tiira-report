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

from tiiradataframe import *
from tiiraplot import *
from tiiramap import *

from jinja2 import Environment, FileSystemLoader
import numpy as np
import pandas as pd
import argparse
import sys

template_file_name = 'lly_report.html'


class Report(object):

    def __init__(self, figures, tables, updated):
        self.figures = figures
        self.tables = tables
        self.updated = updated
        self.data = dict(figures=figures, tables=tables, updated=updated)

    def compose(self):
        file_loader = FileSystemLoader('templates')
        env = Environment(loader=file_loader)
        template = env.get_template(template_file_name)
        output = template.render(data=self.data)
        return output


def main(df):
        plotdata = {}
        figures, tables = [], []

        # REPORT PLOTTING
        # sort keys yksilosumma, havaintorivisumma

        columns = {
            'havainnot': ['havaintorivisumma', 'Tiiraan ilmotetut havaintorivit '],
            'yksilot':  ['yksilosumma', 'Tiiraan ilmotetut yksilöt ']
        }
        for days in [7, 30]:
            for key, value in columns.items():
                plotkey = str(days) + key
                x = df.pipe(filter_submit_period, days=days) \
                    .pipe(groupbylaji) \
                    .pipe(sort, sortkey=value[0]).head(15)
                # drop all columns but laji and aggregate
                plotdata[plotkey] = x[['laji', value[0]]]
                title = value[1] + str(days) + ' päivän aikana'

                s, d = (SumChart(data = plotdata[plotkey], title=title).embedded())
                figures.append(dict(script=s, div=d))

            plotdata[str(days) + 'tallentajat'] = df.pipe(filter_submit_period, days=days) \
                .pipe(groupbysubmitter) \
                .pipe(sort, sortkey='havaintoriviä').head(5)

            title = 'Ahkerimmat tallentajat ' + str(days) + ' päivän aikana'
            d = pd.DataFrame.to_html(plotdata[str(days) + 'tallentajat'], index=False, classes='submittertable')
            # s, d = (TableChart(data = plotdata[str(days) + 'tallentajat'], title = title).embedded())
            tables.append(dict(table=d, title=title))

        report = Report(figures, tables, datetime.now().strftime("%d.%m.%Y klo %H:%M")).compose()

        # MAPS PLOTTING
        gdf = df.pipe(addgeometries, observer_location=True)

        for days in [7, 30]:
            mapdata = gdf.pipe(filter_submit_period, days=days)
            map_filename = f'lly_{days}_days.png'
            Map.plot(mapdata, 'reports/maps/'+map_filename)
        print(datetime.now(), 'kartat valmiit')

        try:
            with open('reports/report.html', 'w') as r:
                r.write(report)
            print(datetime.now(), 'raportti valmis')
        except Exception as e:
            sys.exit(1)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Tee raportti Tiira-data csv:stä")
    # parser.add_argument("-d", "--days", type=int, help="show days past (oletus 7)", default=7)
    parser.add_argument("-f", "--filename", type=str, help="csv-tiedoston nimi (oletus downloader/tiira.csv)", default="downloader/tiira.csv")
    args = parser.parse_args()
    # main(days_past=args.days, csv_filename=args.filename)
    try:
        df = read_csv(args.filename)
    except IOError as e:
        print(f'virhe tiedoston {args.filename} avaamisessa', e)
        sys.exit(1)
    main(df)
# <3 pandas & bokeh & jinja2
