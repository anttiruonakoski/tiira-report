#!/usr/bin/env python3
# coding=utf-8

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
import argparse, sys
# Va,ka blu-users. Connect ja send:

def read_csv(csv_file='downloader/tiira.csv'):

    def finnish_date_converter(x):
        """convert Finnish date format dd.mm.yyyy t ISO-8601"""
        if x:  
            return pd.to_datetime(x, format='%d.%m.%Y')

    parse_dates = ['Tallennusaika']
    #dtypes = {'Määrä': np.int32} # ei voi käyttää kts alta
    df = pd.read_csv(csv_file, sep='#', parse_dates=parse_dates, keep_default_na=True, converters={'Pvm1': finnish_date_converter, 'Pvm2': finnish_date_converter})    
    #tiiran muodostamassa csv-tiedostossa 0-havaintojen yksilömäärä kirjoitettu tyhjänä 'Määrä' sarakkeena. täytetään nollat.
    df['Määrä'] = df['Määrä'].fillna(0)   
    return df

def begin_time(days):    
    s = pd.Timedelta(-days, unit='d') + pd.datetime.now()
    return s

def recentdays(days=7):
    return df['Tallennusaika'] > begin_time(days)
   
def groupbylaji(df):
    f = df.groupby(['Laji'], as_index=False, sort=False).agg({'Määrä': sum, 'Havainto id': 'count'})
    f.columns = ['laji','yksilosumma','havaintorivisumma']
    return f

def groupbysubmitter(df):
    f = df.groupby(['Tallentaja'], as_index=True, sort=False).agg({'Havainto id': 'count'})
    return f    

def sort(df,sortkey):
    return df.sort_values(by=[sortkey],ascending=False);

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Generate a datetime limited pandas.py dataframe")
    parser.add_argument("-d", "--days", type=int, help="show days past (default 7)", default=7)
    parser.add_argument("-f", "--filename", type=str, help="downloaded file name (default tiira.csv)", default="tiira.csv")
    args = parser.parse_args()
    #main(days_past=args.days, csv_filename=args.filename)
    try:
        df = read_csv(args.filename)
    except IOError as e:
        print(f'virhe tiedoston {args.filename} avaamisessa', e)
        sys.exit(1)

    h = df[recentdays(args.days)] \
                                .pipe(groupbylaji) \
                                .pipe(sort, sortkey='yksilosumma')

    t = df[recentdays(args.days)] \
                                .pipe(groupbysubmitter) \
                                .pipe(sort, sortkey='Havainto id')

    desc = df.describe(include=[np.number,np.datetime64])

    #print('full\n', df.describe(include=[np.number,np.datetime64]))
    pd.set_option('float_format', '{:.1f}'.format)
    print(f'{args.days} days\n',
        desc)
      
    print(h.head(2), h.tail(2), t.head(10)) 

    #print (df.loc[df[''].isna()].filter(items=['Havainto id', 'Laji', 'Määrä']))    
   