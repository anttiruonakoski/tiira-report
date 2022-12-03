from dataclasses import dataclass, asdict
import time
import sys
import pickle
import re
from requests import Session
from datetime import datetime, timedelta
from os import path


class Downloader:
    def __init__(self, credentials: dict, options: dict) -> None:

        if not credentials:
            raise ValueError("Kirjatumistunnukset puuttuvat")
        if not options:
            options = DefaultOptions().get()
        self.credentials = credentials
        self.options = options

    def get_session(self):
        with Session() as sess:
            try:
                if time.time() - path.getmtime(absname("cookiefile")) > 600:
                    print(
                        datetime.now(),
                        "\tYli 10 minuuttia vanha istunto. Kirjaudutaan uuteen istuntoon.",
                    )
                    self.login(self.credentials, sess)
                    with open(absname("cookiefile"), "wb") as f:
                        pickle.dump(sess.cookies, f)
                else:
                    with open(absname("cookiefile"), "rb") as f:
                        cookies = pickle.load(f)
                        sess.cookies = cookies
            except IOError as e:
                print(
                    datetime.now(),
                    "\tEi tiedostoa 'cookiefile'. Kirjaudutaan uuteen istuntoon.",
                    e,
                )
                self.login(self.credentials, sess)
                with open(absname("cookiefile"), "wb") as f:
                    pickle.dump(sess.cookies, f)
        self.session = sess
        return sess

    def login(self, credentials: dict, session: Session) -> None:
        # kirjaudutaan ja noudetaan eväste
        # Va,ka blu-users. Connect ja send:
        url = self.options["URL"] + "/index.php"
        post_data = {
            "tunnus": credentials["TUNNUS"],
            "salasana": credentials["SALASANA"],
            "login": "KIRJAUDU",
        }
        try:
            session.post(url, data=post_data, timeout=10)
            print(datetime.now(), "\tKirjauduttu ja eväste tallennettu")
        except Exception as e:
            print("Kirjautuminen epäonnistui", e)
            sys.exit(1)

    def download_last_days_period(self, days: int, alue="23"):

        now = datetime.now()
        delta = timedelta(days=days)
        start = now - delta
        TALLENNUS_ALKUPVM = f"{start:%d.%m.%Y}"
        TALLENNUS_LOPPUPVM = ""
        ALUE = f"{alue}"

        self.print_start_info()

        url_parts = [
            self.options["URL"],
            self.options["ALKU"],
            "kunta=",
            self.options["KUNTA"],
            "&paikka=",
            self.options["PAIKKA"],
            "&paivamaara=3",  # 3=tallennuspvm, 1=havaintopvm?
            "&paivamaara_a=",
            self.options["ALKUPVM"],
            "&paivamaara_l=",
            self.options["LOPPUPVM"],
            "&paivamaara_tal_a=",
            TALLENNUS_ALKUPVM,
            "&paivamaara_tal_l=",
            TALLENNUS_LOPPUPVM,
            "&alue=",
            ALUE,
            "&qorde=&valinta=&omatilm=&omathav=&yhdistyslataus=1&yksmaara=&fi_rari=&fi_aika=&fi_maara=&al_rari=&\
            al_aika=&al_maara=&piilota_poistetut=on&piilota_koontialkuper=on",
            "&rajoitus=",
            self.options["RAJOITUS"],
            "&atlaskrakki=&lyhenne=nimi&taytto=kylla&summarivi=ei",
        ]
        url = "".join(url_parts)
        self.url = url
        return url

    def download_period(self):

        self.print_start_info()

        url_parts = [
            self.options["URL"],
            self.options["ALKU"],
            "kunta=",
            self.options["KUNTA"],
            "&paikka=",
            self.options["PAIKKA"],
            "&paivamaara=3",  # 3=tallennuspvm, 1=havaintopvm?
            "&paivamaara_a=",
            self.options["ALKUPVM"],
            "&paivamaara_l=",
            self.options["LOPPUPVM"],
            "&paivamaara_tal_a=",
            self.options["TALLENNUS_ALKUPVM"],
            "&paivamaara_tal_l=",
            self.options["TALLENNUS_LOPPUPVM"],
            "&alue=",
            self.options["ALUE"],
            "&qorde=&valinta=&omatilm=&omathav=&yhdistyslataus=1&yksmaara=&fi_rari=&fi_aika=&fi_maara=&al_rari=&\
            al_aika=&al_maara=&piilota_poistetut=on",
            "&piilota_koontialkuper=",
            self.options["PIILOTA_KOONTIALKUPER"],
            "&rajoitus=",
            self.options["RAJOITUS"],
            "&atlaskrakki=&lyhenne=nimi&taytto=kylla&summarivi=ei",
        ]
        url = "".join(url_parts)
        self.url = url
        return url

    def download(self) -> str:
        try:
            csv_raw = self.session.get(self.url, timeout=600)
            csv_raw.raise_for_status()
        except Exception as e:
            print("Virhe csv-tiedoston osoitteen hakemisessa. \n", e)
            sys.exit(1)

        filepattern = r"omatcsvt\/.*.txt"
        downloadable_file = re.findall(
            filepattern, csv_raw.text
        )  # omatcsvt/124_csv_YJ4ofuUwsp.txt
        final_url = self.options["URL"] + "/" + downloadable_file[0]
        print(f"Lopullinen latausurl: {final_url}")

        try:
            csv = self.session.get(final_url)
            csv.raise_for_status()
        except Exception as e:
            print("Virhe csv-tiedoston latauksessa. \n", e)
            sys.exit(1)
        return csv.text

    def print_start_info(self):
        print(
            datetime.now(),
            "\talkupvm ",
            self.options["TALLENNUS_ALKUPVM"],
            "loppupvm ",
            self.options["TALLENNUS_LOPPUPVM"],
        )


@dataclass
class DefaultOptions:
    URL: str = "https://www.tiira.fi"
    ALKU: str = "/csv_omat.php?laji=&valtkun=&"
    TALLENNUS_ALKUPVM: str = ""
    TALLENNUS_LOPPUPVM: str = ""
    ALKUPVM: str = ""
    LOPPUPVM: str = ""
    KUNTA: str = ""
    PAIKKA: str = ""
    RAJOITUS: str = "5"  # '0' kaikki, '5' salaamattomat
    ALUE: str = "23"  # Lapin lintutieteellinen yhdistys
    PIILOTA_KOONTIALKUPER: str = "on"

    def get(self):
        return asdict(self)


@dataclass
class YearOptions(DefaultOptions):
    year: int = datetime.now().year
    half_year: int = 0
    PIILOTA_KOONTIALKUPER: str = ""

    def __post_init__(self):
        self.PIILOTA_KOONTIALKUPER = ""
        if self.half_year == 0:
            self.TALLENNUS_ALKUPVM = "1.1." + str(self.year)
            self.TALLENNUS_LOPPUPVM = "31.12." + str(self.year)
        # keväisin tallennetaan havaintoja enemmän, joten jaetaan vuosi toukokuun lopusta, jotta latausten rivimäärät tasoittuisivat
        if self.half_year == 1:
            self.TALLENNUS_ALKUPVM = "1.1." + str(self.year)
            self.TALLENNUS_LOPPUPVM = "31.5." + str(self.year)
        if self.half_year == 2:
            self.TALLENNUS_ALKUPVM = "1.6." + str(self.year)
            self.TALLENNUS_LOPPUPVM = "31.12." + str(self.year)


def absname(filename) -> str:
    cp = path.dirname(path.abspath(__file__))
    return path.join(cp, filename)


if __name__ == "__main__":
    pass
