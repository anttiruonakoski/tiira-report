## Tiira-report

Python tools for [Tiira](https://www.tiira.fi) bird observation data reporting and visualization. Illustrative report is published at (https://www.lly.fi/tiira-raportti) 
  
Components:

- tiiradownloader: download and save data as a csv-file

- tiirareport: generate a web page  
	+ tiiraplot: plot diagrams
	+ tiiramap: plot maps
	+ report template: Jinja2 template for report HTML

#### Installation & requirements

`git clone https://github.com/anttiruonakoski/tiira-report`

Supported python version >= 3.6.
To install requirements

`pip3 install -r requirements.txt` 

#### After Installation

`cp downloader/credentials.example credentials.txt`  
Input correct login credentials

#### Usage example

`python3 downloader/tiira_downloader.py -d 30 -f tiira.csv`
`python3 tiirareport.py -f tiira.csv`

#### License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details


