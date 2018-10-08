#!/usr/bin/env python3

"""tiiradataframe.py: Generate a datetime limited pandas.py dataframe with a few aggregates from Tiira priviledged user CSV-download data."""

__author__ = "Antti Ruonakoski"
__copyright__ = "Copyright 2018"
__credits__ = ["Antti Ruonakoski"]
__license__ = "MIT"
__version__ = ""
__maintainer__ = "Antti Ruonakoski"
__email__ = "aruonakoski@gmail.com"
__status__ = "Development"

import numpy as np
import pandas as pd

class TiiraData(csv_file):

    parse_dates = ['Tallennusaika','Pvm1','Pvm2']

    df = pd.read_csv('downloader/testidata_u_07102018.csv',sep='#',parse_dates=parse_dates)
    df.dtypes

    pd.set_option('float_format', '{:.1f}'.format)
    df.describe(include=[np.number,np.datetime64])
    df.head(2)

    def timeframe(data, days=7):
        
        #get data start n days ago, end now
        start = pd.Timedelta(-days, unit='d') + pd.datetime.now()
        #print(f'alku {start}')
        dataframe = data[(data['Tallennusaika'] > start)]
        return dataframe

    df_last_7 = timeframe(df,7)
    df_last_30 = timeframe(df,30)

    pd.set_option('float_format', '{:.1f}'.format)
    df_last_7.describe(include=[np.number,np.datetime64])
    #df_last_30.describe(include=[np.number,np.datetime64])


    data7 = timeframe(df,7).groupby(['Laji'], as_index=False, sort=False).agg({'Määrä': sum, 'Havainto id': 'count'})
    data7.columns = ['laji','yksilosumma','havaintorivisumma']

    data7

    pd.set_option("display.precision",0)

    sum_species = data7.sort_values(by=['havaintorivisumma'],ascending=False);

    #sum_species_30 = timeframe(df,30).groupby(['Laji'], as_index=False, sort=False)[["yksilosumma"]].sum().sort_values(by=['yksilosumma'],ascending=False);

    sum_species.head(10)


    sum_ind = timeframe(df,30)['Määrä'].sum()

    print (f'yksilöitä 30 päivän aikana yhteensä {sum_ind:.0f}')
    print ('tallentajia',df['Tallentaja'].nunique())

    top_recorders = df_last_7.groupby('Tallentaja', as_index=True, sort=False).agg({'Havainto id': 'count'}).sort_values(by=['Havainto id'],ascending=False)

    top_recorders.columns = ['Havaintorivejä']
    top_recorders.head(3)
    #print (f'{top_recorders.head(3)}')

    timeframe(df,15).describe()

if __name__ == "__main__":

    output = Report()
    print (output.write())





