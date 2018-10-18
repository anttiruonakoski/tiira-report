#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""tiiradownloader.py: Authenticate and download a csv-file from tiira.fi."""

__author__ = "Antti Ruonakoski"
__copyright__ = "Copyright 2018"
__credits__ = ["Antti Ruonakoski"]
__license__ = "MIT"
__version__ = ""
__maintainer__ = "Antti Ruonakoski"
__email__ = "aruonakoski@gmail.com"
__status__ = "Development"

from os import remove, path
import time
import sys
import html
import re
import requests
import pickle
import argparse
from datetime import datetime, timedelta

wait = 5
cp = path.dirname(path.abspath(__file__))


def absname(filename):
    return path.join(cp, filename)


URL = 'https://www.tiira.fi'
ALKU = '/csv_omat.php?laji=&valtkun=&'

HAVALKUPVM = ''
HAVLOPPUPVM = ''
TALLENNUS_ALKUPVM = ''
TALLENNUS_LOPPUPVM = ''
ALKUPVM = ''
LOPPUPVM = ''
KUNTA = ''
PAIKKA = ''
RAJOITUS = '5'  # '0' kaikki, '5' salaamattomat
ALUE = '23'  # Lapin lintutieteellinen yhdistys

# ALKUVUOSI = sys.argv[1]
# LOPPUVUOSI = sys.argv[2]

days_past = 7  # default downloaded period in days


def login(credentials, session):

    # kirjaudutaan ja noudetaan eväste
    # Va,ka blu-users. Connect ja send:
    url = URL + '/index.php'
    post_data = {
        'tunnus': credentials['TUNNUS'],
        'salasana': credentials['SALASANA'],
        'login': 'KIRJAUDU'
    }
    try:
        r = session.post(url, data=post_data, timeout=10)
        print(datetime.now(), '\tKirjauduttu ja eväste tallennettu')
        return r.cookies
    except Exception as e:
        print('Kirjautuminen epäonnistui', e)
        sys.exit(1)


def new_session(credentials):
    s = requests.session()
    try:
        if time.time() - path.getmtime(absname('cookiefile')) > 600:
            print(datetime.now(), '\tYli 10 minuuttia vanha istunto. Kirjaudutaan uuteen istuntoon.')
            login(credentials, s)
            with open(absname('cookiefile'), 'wb') as f:
                pickle.dump(s.cookies, f)
        else:
            with open(absname('cookiefile'), 'rb') as f:
                cookies = pickle.load(f)
                s.cookies = cookies
    except IOError as e:
        print(datetime.now(), '\tEi tiedostoa \'cookiefile\'. Kirjaudutaan uuteen istuntoon.', e)
        login(credentials, s)
        with open(absname('cookiefile'), 'wb') as f:
            pickle.dump(s.cookies, f)
    return s

# TBD

# def download_year(years):
#     ALKUPVM='1.1.'
#     LOPPUPVM='31.12.'
#     for vuosi in range(int(ALKUVUOSI),int(LOPPUVUOSI)+1):
#
#         TALLENNUS_ALKUPVM=ALKUPVM+str(vuosi)
#         TALLENNUS_LOPPUPVM=LOPPUPVM+str(vuosi)
#         print ("alkupvm ", TALLENNUS_ALKUPVM, "loppupvm ", TALLENNUS_LOPPUPVM)


def download_period(days, session, alue='23'):

    now = datetime.now()
    delta = timedelta(days=days)
    start = now - delta
    TALLENNUS_ALKUPVM = f'{start:%d.%m.%Y}'
    TALLENNUS_LOPPUPVM = ''
    ALUE = f'{alue}'

    print(datetime.now(), "\talkupvm ", TALLENNUS_ALKUPVM, "loppupvm ", TALLENNUS_LOPPUPVM)

    url_parts = [
        URL,
        ALKU,
        'kunta=', KUNTA,
        '&paikka=', PAIKKA,
        '&paivamaara=3',  # 3=tallennuspvm, 1=havaintopvm?
        '&paivamaara_a=', ALKUPVM,
        '&paivamaara_l=', LOPPUPVM,
        '&paivamaara_tal_a=', TALLENNUS_ALKUPVM,
        '&paivamaara_tal_l=', TALLENNUS_LOPPUPVM,
        '&alue=', ALUE,
        '&qorde=&valinta=&omatilm=&omathav=&yhdistyslataus=1&yksmaara=&fi_rari=&fi_aika=&fi_maara=&al_rari=&al_aika=&al_maara=&piilota_poistetut=on&piilota_koontialkuper=on',
        '&rajoitus=', RAJOITUS,
        '&atlaskrakki=&lyhenne=nimi&taytto=kylla&summarivi=ei']
    url = ''.join(url_parts)

    try:
        csv_raw = session.get(url)
    except Exception as e:
        print(e)

    filepattern = 'omatcsvt\/.*.txt'
    downloadable_file = (re.findall(filepattern, csv_raw.text))  # omatcsvt/124_csv_YJ4ofuUwsp.txt
    url = URL + '/' + downloadable_file[0]
    print('lopullinen latausurl ', url)

    try:
        csv = session.get(url)
    except Exception as e:
        print(e)
    return csv.text


def main(days_past, csv_filename, alue):

    credentials = {
            'TUNNUS': '',
            'SALASANA': ''
        }

    with open(absname('credentials.txt'), 'r') as fp:
        for i in ['TUNNUS', 'SALASANA']:
            credentials[i] = fp.readline().strip()

    session = new_session(credentials)

    for chance in range(3):
        try:
            print(datetime.now(), f'\tLadataan csv-tiedosto {days_past} päivän ajalta')
            csv = download_period(days_past, session, alue)
            if len(csv.split('\r\n', 1)[0]) < 380 or len(csv.split('\r\n', 1)[0]) > 410:
                # LRCF newlines
                # normal tiira csv-file first line length for 1st line is 391, depends on linefeed characters. allows minor csv-format change
                print(datetime.now(), '\tViallinen csv-tiedosto tai vanhentunut istunto. Kirjaudutaan ja yritetään uudelleen. kerta: ', chance)
                time.sleep(wait)
                session = new_session(credentials)
            else:
                with open(csv_filename, 'w', newline='\n') as f:
                    csv_unescaped = html.unescape(csv)
                    csv_unix_newlines = '\n'.join(csv_unescaped.splitlines())
                    f.write(csv_unix_newlines)
                    # converts newlines
                    # converts to utf-8 because it's native text write encoding in Python.
                    # html entities such as emojis should be unescaped
                    # tbd check malformed rows (extra '#' inputted in tiira text field). doesn't matter with pandas csv impoter, but effects SQL copy commands
                    print(datetime.now(), '\tcsv-tiedosto tallennettu onnistuneesti')
                break
        except Exception as e:
            print(f'error {e}')
            sys.exit(1)
    print(datetime.now(), '\tLataus päättyi')


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Kirjaantuu Tiiraan ja lataa csv-tiedoston tallennusajan mukaan")
    parser.add_argument("-d", "--days", type=int, help="kuinka monta päivää taaksepäin nykyhetkestä  (oletus 7)", default=7)
    parser.add_argument("-f", "--filename", type=str, help="ladattavan tiedoston nimi (oletus tiira.csv)", default="tiira.csv")
    parser.add_argument("-a", "--area", type=int, help="Lintutieteellisen yhdistyksen aluekoodi (oletus 23)", default="23")
    args = parser.parse_args()
    main(days_past=args.days, csv_filename=args.filename, alue=args.area)