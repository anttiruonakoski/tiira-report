from datetime import datetime, timedelta

# import numpy as np
import csv
import pandas as pd
import argparse
import sys

# import geopandas as gpd
# from shapely.geometry import Point


def read_csv(csv_file="downloader/tiira.csv") -> pd.DataFrame | None:
    def finnish_date_converter(x):
        """convert Finnish date format dd.mm.yyyy to ISO-8601"""
        if x:
            try:
                return pd.to_datetime(x, format="%d.%m.%Y", errors="coerce")
            except Exception:
                # Tiira csv date can include zero day or month value
                dateparts = x.split(".")
                date, format = [], []
                try:
                    for num, part in enumerate(["%d", "%m"]):
                        if int(dateparts[num]):
                            format.append(part)
                            date.append(dateparts[num])
                except Exception as e:
                    print(e)
                format = ".".join(format) + ".%Y"
                date = ".".join(date) + "." + dateparts[2]
                d = pd.to_datetime(date, format=format)
                return d

    parse_dates = ["Tallennusaika"]
    # dtypes = {'Määrä': np.int32} # ei voi käyttää kts alta
    df = pd.read_csv(
        csv_file,
        sep="#",
        parse_dates=parse_dates,
        keep_default_na=True,
        converters={"Pvm1": finnish_date_converter, "Pvm2": finnish_date_converter},
        low_memory=False,
        # engine='python',
        # on_bad_lines=handle_bad_line,
        on_bad_lines="warn",
        # tämä on tärkeä, muuten rivit, joilla on lainausmerkki ohitetaan
        quoting=csv.QUOTE_NONE,
    )
    # tiiran muodostamassa csv-tiedostossa 0-havaintojen yksilömäärä kirjoitettu tyhjänä 'Määrä' sarakkeena.
    # täytetään nollat.
    df["Määrä"] = df["Määrä"].fillna(0)
    return df


def handle_bad_line(bad_line: list) -> None:
    print(bad_line)
    sys.exit(1)
    return None


def main(filename: str):
    """with open(filename, 'r') as f:
    for l in f:
        if len(l) < 10:
            print(l)"""

    df = read_csv(filename)
    print(df.shape[0])
    print(df.describe())
    # print(df[df['Havainto id'].isnull()])
    # print(df.iloc[30210:30215])

    # 2013 id 9962459 ylimääräinen lf, tee converter, joka poistaa vapaatekstikentistä lft


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Lue Tiirasta ladattu CSV-tiedosto dataframeen ja mahdollisesti dumppaa se Postgres-tietokantaan"
    )
    parser.add_argument(
        "-f",
        "--filename",
        type=str,
        help="downloaded file name (default tiira.csv)",
        default="tiira.csv",
    )

main(**vars(parser.parse_args()))
