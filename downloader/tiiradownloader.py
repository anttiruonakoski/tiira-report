#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""tiiradownloader.py: Authenticate and download a csv-file from tiira.fi."""

__author__ = "Antti Ruonakoski"
__copyright__ = "Copyright 2018-2022"
__credits__ = ["Antti Ruonakoski"]
__license__ = "MIT"
__version__ = ""
__maintainer__ = "Antti Ruonakoski"
__email__ = "aruonakoski@gmail.com"
__status__ = "Development"

import time
import sys
import html
import argparse
from datetime import datetime
from tiiradl import Downloader, DefaultOptions, YearOptions, absname

wait = 5

# TBD

# def download_year(years):
#     ALKUPVM='1.1.'
#     LOPPUPVM='31.12.'
#     for vuosi in range(int(ALKUVUOSI),int(LOPPUVUOSI)+1):
#
#         TALLENNUS_ALKUPVM=ALKUPVM+str(vuosi)
#         TALLENNUS_LOPPUPVM=LOPPUPVM+str(vuosi)
#         print ("alkupvm ", TALLENNUS_ALKUPVM, "loppupvm ", TALLENNUS_LOPPUPVM)


def main(
    days: int,
    filename: str,
    bl_area: int,
    year_recorded=None,
    start_date=None,
    end_date=None,
    include_hidden=False,
    half_year=0
):

    if (include_hidden):
        RAJOITUS = '0'
    else:
        RAJOITUS = '5'
    csv_filename = filename
    credentials = {"TUNNUS": "", "SALASANA": ""}

    with open(absname("credentials.txt"), "r") as fp:
        for i in ["TUNNUS", "SALASANA"]:
            credentials[i] = fp.readline().strip()

    dl = Downloader(credentials=credentials, options={})

    if year_recorded:
        if year_recorded < 2006 or year_recorded > datetime.now().year:
            print('Tarkista vuosi. Tiira avattiin 2006.')
            sys.exit(1)
        dl.options = YearOptions(ALUE=str(bl_area), year=year_recorded, half_year=half_year, RAJOITUS=RAJOITUS).get()
        dl.download_period()
        match half_year:
            case 0:
                half_year_part = ''
            case 1:
                half_year_part = '_alkuvuosi'
            case 2:
                half_year_part = '_loppuvuosi'
            case _:
                half_year_part = ''

        print(datetime.now(), f"\tLadataan csv-tiedosto tallennusvuosi {year_recorded} {half_year_part}.")
        csv_filename = f"{csv_filename.split('.')[0]}_tallennusvuosi_{year_recorded}{half_year_part}.csv"
        print(csv_filename)
    elif days:
        dl.options = DefaultOptions(ALUE=str(bl_area), RAJOITUS=RAJOITUS).get()
        dl.download_last_days_period(days)
        print(datetime.now(), f"\tLadataan csv-tiedosto viimeisen {days} päivän ajalta.")
    else:
        print("Ei tallennusvalintoja")
        sys.exit(1)

    dl.get_session()

    for chance in range(2):
        try:
            csv = dl.download()
            if len(csv.split("\r\n", 1)[0]) < 380 or len(csv.split("\r\n", 1)[0]) > 410:
                # LRCF newlines
                # normal tiira csv-file first line length for 1st line is 391, depends on linefeed characters.
                # allows minor csv-format change
                print(
                    datetime.now(),
                    "\tViallinen csv-tiedosto tai vanhentunut istunto. Kirjaudutaan ja yritetään uudelleen. kerta: ",
                    chance,
                )
                time.sleep(wait)
                dl.get_session()
            else:
                with open(csv_filename, "w", newline="\n") as f:
                    csv_unescaped = html.unescape(csv)
                    csv_unix_newlines = "\n".join(csv_unescaped.splitlines())
                    f.write(csv_unix_newlines)
                    # converts newlines
                    # converts to utf-8 because it's native text write encoding in Python.
                    # html entities such as emojis should be unescaped
                    # tbd check malformed rows (extra '#' inputted in tiira text field).
                    # doesn't matter with pandas csv impoter, but effects SQL copy commands
                    print(datetime.now(), "\tcsv-tiedosto tallennettu onnistuneesti")
                break
        except Exception as e:
            print(f"error {e}")
            sys.exit(1)
    print(datetime.now(), "\tLataus päättyi")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Kirjaantuu Tiiraan ja lataa csv-tiedoston tallennusajan mukaan."
    )
    parser.add_argument(
        "-yr",
        "--year-recorded",
        type=int,
        help="Ladataan havainnot yhdeltä tallennusvuodelta (oletus kuluva vuosi)",
    )
    parser.add_argument(
        "-d",
        "--days",
        type=int,
        help="Ladataan havainnot kuluvasta päivästä annettu määrä päiviä taaksepäin. (oletus 7)",
    )
    parser.add_argument(
        "--include-hidden",
        action='store_true',
        help="Salatut sisältyvät lataukseen (oletus ei).",
    )
    parser.add_argument(
        "--half-year",
        type=int,
        help="Ladataan puoli vuotta kerrallaan (oletus 0 eli koko vuosi). 1=alkuvuosi. 2=loppuvuosi.",
    )
    parser.add_argument(
        "-f",
        "--filename",
        type=str,
        help="Tallennettavan csv-tiedoston nimi (oletus tiira.csv)",
        default="tiira_lly.csv",
    )
    parser.add_argument(
        "-a",
        "--bl-area",
        type=int,
        help="Lintutieteellisen yhdistyksen aluekoodi (oletus 23)",
        default="23",
    )
    args = parser.parse_args()
    main(**vars(args))
