#!/usr/bin/env python3

"""tiiradataframe.py: functions for Tiira-specific pandas dataframe"""

__author__ = "Antti Ruonakoski"
__copyright__ = "Copyright 2018"
__credits__ = ["Antti Ruonakoski"]
__license__ = "MIT"
__version__ = ""
__maintainer__ = "Antti Ruonakoski"
__email__ = "aruonakoski@gmail.com"
__status__ = "Development"

from datetime import datetime, timedelta
import numpy as np
import pandas as pd
# Va,ka blu-users. Connect ja send:

def begin_time(days=7):    
    s = pd.Timedelta(-days, unit='d') + pd.datetime.now()
    return s

def recentdays(days=7):
    return df['Tallennusaika'] > begin_time(days)
#df[recentdays(11)].describe(include=[np.number,np.datetime64])

def read_csv(csv_file='downloader/tiira.csv'):
    parse_dates = ['Tallennusaika','Pvm1','Pvm2']
    df = pd.read_csv(self.csv_file, sep='#', parse_dates=parse_dates)    
    return df
   
def group():
    return self.df.groupby(['Laji'], as_index=False, sort=False).agg({'Määrä': sum, 'Havainto id': 'count'}) 


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Generate a datetime limited pandas.py dataframe")
    #parser.add_argument("-d", "--days", type=int, help="download days past (default 7)", default=7)
    parser.add_argument("-f", "--filename", type=str, help="downloaded file name (default tiira.csv)", default="tiira.csv")
    args = parser.parse_args()
    #main(days_past=args.days, csv_filename=args.filename)
    try:
        tiiradata = read_csv(args.filename)
    except IOError:
        print('unable to open file')

    data_7_days.columns = ['laji','yksilosumma','havaintorivisumma']

    sum_species = data_7_days.sort_values(by=['havaintorivisumma'],ascending=False);
    print(sum_species.head(10))

    #top_recorders = timeframe(df,7).groupby('Tallentaja', as_index=True, sort=False).agg({'Havainto id': 'count'}).sort_values(by=['Havainto id'],ascending=False)





