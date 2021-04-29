import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.animation import FuncAnimation

df = pd.read_csv('https://raw.githubusercontent.com/Oryngaliyev21/covid-19-data/master/public/data/vaccinations/vaccinations.csv')

d = {}
data = pd.DataFrame(d)
for i, item in enumerate(df.location.tolist()):
  if item=='World':
    data = data.append(df.loc[[i]], ignore_index=True)

time = data.date.tolist()
total_vaccinations = data.total_vaccinations.tolist()
people_vaccinated = data.people_vaccinated.tolist()
people_fully_vaccinated = data.people_fully_vaccinated.tolist()

np_time = np.array([np.datetime64(x) for x in time])
np_v = np.array(total_vaccinations)
np_pv = np.array(people_vaccinated)
np_pfv = np.array(people_fully_vaccinated)

import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.dates import DateFormatter
from matplotlib.ticker import FuncFormatter, MultipleLocator

def animate(i):
    data = df.loc[date(2020, 2, 23):, :].iloc[:int(i+1)] #select data range
    p_us = axarr.plot(data.index, data['US'],
                      label='US', color='tab:blue')
    p_italy = axarr.plot(data.index, data['Italy'],
                         label='Italy', color='tab:orange')
    p_cn = axarr.plot(data.index, data['China'],
                      label='China', color='tab:green')
    p_spain = axarr.plot(data.index, data['Spain'],
                         label='Spain', color='tab:red')
    p_germany = axarr.plot(data.index, data['Germany'],
                           label='Germany', color='tab:purple')
    p_france = axarr.plot(data.index, data['France'],
                          label='France', color='tab:brown')
    plt.legend(['US', 'Italy', 'China', 'Spain', 'Germany', 'France'])

ctry_ts = animation.FuncAnimation(fig, animate, frames=51, repeat=True,
                                  interval=500, repeat_delay=2000)
