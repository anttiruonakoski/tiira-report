## Tiira-report

Python tools for [Tiira](https://www.tiira.fi) bird observation data reporting and visualization. Demonstrative report is published at https://www.lly.fi/havainnot/tiira-raportti 
  
Components and main libraries used:

- tiiradownloader: download and save data as a csv-file  
	*currently supports only regional society Tiira admin downloads* 

- tiirareport: generate a web page
	+ tiiradataframe: functions for Tiira-specific pandas and geopandas dataframes 
	+ tiiraplot: plot potentially interactive diagrams - *Bokeh*
	+ tiiramap: plot static maps - *matplotlib, rasterio*
	+ templates: template for report HTML - *Jinja2*

- Jupyter notebook examples how-to manipulate, analyze and utilize data. To be done.

- static: css, basemaps, etc.


#### Installation & requirements

`git clone https://github.com/anttiruonakoski/tiira-report`

Supported python version >= 3.6.
To install requirements

`pip3 install -r requirements.txt` 


#### After Installation

`cp downloader/credentials.example credentials.txt`  
Input correct login credentials


#### Usage example

```
python3 downloader/tiira_downloader.py -d 30 -f tiira.csv
python3 tiirareport.py -f tiira.csv
```


#### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details


