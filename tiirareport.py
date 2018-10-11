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
import tiiradataframe

class Report(object, plotdata):

    def __init__(self, plotdata, filename):          
        self.plotdata = plotdata
        self.filename = filename
        
    def compose(self):    
        file_loader = FileSystemLoader('templates')
        env = Environment(loader=file_loader)  
        template = env.get_template(template_file_name)
        output = template.render(plotdata=plotdata)
        return output

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Generate Tiira report") 
    #parser.add_argument("-d", "--days", type=int, help="download days past (default 7)", default=7)
    parser.add_argument("-f", "--filename", type=str, help="downloaded file name (default tiira.csv)", default="tiira.csv")
    args = parser.parse_args()
    #main(days_past=args.days, csv_filename=args.filename)
    try:
        tiiradata = read_csv(args.filename)
    except IOError:
        print('unable to open file', args.filename)

    plotdata = {}
    figures = {}

    #ACTUAL PLOTTING    

    plotdata['7havainnot'] = tiiradata(recentdays(7)).pipe(
        group,
        sort
    ).head(25)

    plotdata['30havainnot'] = Tiiradata(30).group()

    for k, data in plotdata.items():
        figures[k]* = SumChart(data).embedded()

    plotdata = {}
    plotdata['7tallentajat'] = Tiiradata(7).submitters.head(3)
    plotdata['30tallentajat'] = Tiiradata(30).submitters.head(3)

    for k, value in plotdata.items():
        figures[k]* = SubmitterTable(value)
    
    report = Report(figures).compose()

    with open ('reports/report.html', w) as r:
        r.write(report)

# <3 pandas & bokeh      

