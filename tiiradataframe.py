#!/usr/bin/env python3
# coding=utf-8

"""tiiradataframe.py: functions for Tiira-specific pandas and geopandas dataframes"""

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
import argparse
import sys
import geopandas as gpd
from shapely.geometry import Point
# Va,ka blu-users. Connect ja send:


def read_csv(csv_file='downloader/tiira.csv'):

    def finnish_date_converter(x):
        """convert Finnish date format dd.mm.yyyy to ISO-8601"""
        if x:
            return pd.to_datetime(x, format='%d.%m.%Y', errors='coerce')

    parse_dates = ['Tallennusaika']
    # dtypes = {'Määrä': np.int32} # ei voi käyttää kts alta
    df = pd.read_csv(
        csv_file, sep='#', parse_dates=parse_dates, keep_default_na=True,
        converters={'Pvm1': finnish_date_converter, 'Pvm2': finnish_date_converter}, low_memory=False)
    # tiiran muodostamassa csv-tiedostossa 0-havaintojen yksilömäärä kirjoitettu tyhjänä 'Määrä' sarakkeena.
    # täytetään nollat.
    df['Määrä'] = df['Määrä'].fillna(0)
    return df


def begin_time(days):
    s = pd.Timedelta(-days, unit='d') + datetime.now()
    return s


def recentdays(days=7):
    return df['Tallennusaika'] > begin_time(days)


def filter_submit_period(df, days=7):
    return df[df['Tallennusaika'] > begin_time(days)]


def groupbylaji(df):
    f = df.groupby(['Laji'], as_index=False, sort=False).agg({'Määrä': sum, 'Havainto id': 'count'})
    f.columns = ['laji', 'yksilosumma', 'havaintorivisumma']
    return f


def groupbysubmitter(df):
    f = df.groupby(['Tallentaja'], as_index=False, sort=False).agg({'Havainto id': 'count'})
    f.columns = ['tallentaja', 'havaintoriviä']
    return f


def sort(df, sortkey):
    return df.sort_values(by=[sortkey], ascending=False)


def addgeometries(df, observer_location=True):
    # bird_location not implemented
    if observer_location:
        df['Coordinates'] = list(zip(df['X-koord'], df['Y-koord']))
        df['Coordinates'] = df['Coordinates'].apply(Point)
        gdf = gpd.GeoDataFrame(df, geometry='Coordinates')
        gdf.set_crs(epsg=3067, inplace=True)
    return gdf


def filter_points_not_within_boundaries(tiira_gdf: gpd.GeoDataFrame, mask_file='data/LLY-toimialue.gpkg',
                                        mask_layer='LLY-toimialue') -> gpd.GeoDataFrame:
    try:
        mask_gdf = gpd.read_file(mask_file, layer=mask_layer)
        tiira_gdf = gpd.clip(tiira_gdf, mask_gdf)
    except IOError as e:
        print(f'virhe tiedoston {mask_file} avaamisessa', e)
        sys.exit(1)
    return tiira_gdf


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Generate a datetime limited pandas.py dataframe")
    parser.add_argument(
        "-d", "--days", type=int, help="show days past (default 7)", default=7)
    parser.add_argument(
        "-f", "--filename", type=str, help="downloaded file name (default tiira.csv)", default="tiira.csv")
    args = parser.parse_args()
    # main(days_past=args.days, csv_filename=args.filename)
    try:
        df = read_csv(args.filename)
    except IOError as e:
        print(f'virhe tiedoston {args.filename} avaamisessa', e)
        sys.exit(1)

    # below just for testing functions

    h = df[recentdays(args.days)] \
        .pipe(groupbylaji) \
        .pipe(sort, sortkey='yksilosumma').head(20)

    t = df[recentdays(args.days)] \
        .pipe(groupbysubmitter) \
        .pipe(sort, sortkey='havaintoriviä')

    desc = df.describe(include=[np.number, np.datetime64])

    # print('full\n', df.describe(include=[np.number,np.datetime64]))
    pd.set_option('float_format', '{:.1f}'.format)
    print(f'{args.days} days\n', desc)

    print(h.head(10), h.tail(2), t.head(10))

    #print (df.loc[df[''].isna()].filter(items=['Havainto id', 'Laji', 'Määrä']))
