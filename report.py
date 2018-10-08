import numpy as np
import pandas as pd
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

from bokeh.plotting import figure
from bokeh.io import show, output_file, save
from bokeh.models import ColumnDataSource, LabelSet
from bokeh.layouts import column
from bokeh.resources import CDN
from bokeh.embed import file_html

# Create a blank figure with labels

p = []
periods = {0:7,1:30}

for key,period in periods.items():
    
    data = timeframe(df,period).groupby(['Laji'], as_index=False, sort=False)[["Määrä"]].sum().sort_values(by=['Määrä'],ascending=False).head(25)

    source = ColumnDataSource(data)

    high = data[data['Määrä'] > data['Määrä'].quantile(.9)]
    low = data[data['Määrä'] <= data['Määrä'].quantile(.9)]

    sourcehigh = ColumnDataSource(high)
    sourcelow = ColumnDataSource(low)

    lajit = source.data['Laji'].tolist()[::-1]
    title = f'Tiiraan ilmoitettua yksilöä, viimeiset {period} päivää'

    p.append(figure(plot_width = 640, plot_height = 500, x_axis_type='linear',
               title = title,
               y_range=lajit))

    labels = LabelSet(x='Määrä', y='Laji', text='Määrä', level='glyph',x_offset=5, source=sourcelow, text_font_size='8pt', text_baseline='middle')
    labelshigh = LabelSet(x='Määrä', y='Laji', text='Määrä', level='glyph',x_offset=-30, source=sourcehigh, text_font_size='8pt', text_baseline='middle', text_color='#FFFFFF')
    
    #visual
    p[key].x_range.start = 0
    p[key].toolbar.logo = None
    p[key].toolbar_location = None
    p[key].yaxis.major_tick_line_color = None  # turn off y-axis major ticks
    p[key].yaxis.minor_tick_line_color = None
    p[key].xaxis.minor_tick_line_color = None
    p[key].ygrid.grid_line_color = None
    p[key].toolbar.active_drag = None
    p[key].hbar(y='Laji', right='Määrä', left=0, height=0.75, source=source)
    p[key].add_layout(labels)
    p[key].add_layout(labelshigh)

# Set to output the plot in the notebook
    filename = 'x' + str(key) + '.html'
    output_file(filename, title='Bokeh Plot', mode='cdn', root_dir=None)
    save(p[key])

#save(p[key], 'x.html')
# Show the plot
#show(column(p[0],p[1]))


from jinja2 import Environment, FileSystemLoader
file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader)

template = env.get_template('base.html')
output = template.render()
print(output)
