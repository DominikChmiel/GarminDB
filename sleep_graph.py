import GarminDB
from garmin_db_config_manager import GarminDBConfigManager

from import_garmin import SleepActivityLevels, RemSleepActivityLevels

from datetime import datetime, timedelta, time

import pytz
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import ListedColormap, LinearSegmentedColormap

import math

tz = pytz.timezone('Europe/Berlin')

gDB = GarminDB.GarminDB(GarminDBConfigManager.get_db_params(), 0)

sleep_events = GarminDB.SleepEvents.get_all(gDB)

date_range = [sleep_events[0].timestamp + timedelta(days=-1), sleep_events[-1].timestamp + timedelta(days=2)]

days = (date_range[1] - date_range[0]).days

YSTEP = timedelta(minutes=6)
DAILY_Y = int(timedelta(days=1).total_seconds() / YSTEP.total_seconds())

sleep_data = np.array([[0] * days] * DAILY_Y)
sleep_data.fill(0)


def add_sleep_state(data, start, end, state):
	start_diff = start - datetime.combine(date_range[0].date(), time())
	day = start_diff.days
	start_ind = int((start_diff.total_seconds() % timedelta(days=1).total_seconds()) / YSTEP.total_seconds())
	dur_ind = math.ceil((end - start).total_seconds() / YSTEP.total_seconds())
	for i in range(0, dur_ind):
		xind = (start_ind + i) % DAILY_Y
		yind = day + (start_ind + i) // DAILY_Y
		data[xind, yind] = max(state, data[xind, yind])


# Query total sleep info
sleep = GarminDB.Sleep.get_all(gDB)
sleep = [x for x in sleep if x.start is not None]
print(sleep[0])
for sev in sleep:
	add_sleep_state(sleep_data, sev.start, sev.end, 1)

sleep_data_detail = np.array([[0] * days] * DAILY_Y)
sleep_data_detail.fill(0)
# sleep_data_detail = np.copy(sleep_data)

# Augment data with sleep Events
for ev in sleep_events:
	slevel = RemSleepActivityLevels[ev.event]
	localized = ev.timestamp + tz.localize(ev.timestamp).utcoffset()
	val = slevel.value + 1
	#if localized.weekday() < 5:
	#	val += 5
	if val > 0 and localized.weekday() < 5:
		add_sleep_state(sleep_data_detail, localized, localized + timedelta(hours=ev.duration.hour, minutes=ev.duration.minute), val)


cmap = ListedColormap(["black", (0 / 256, 75 / 256, 160 / 256), (25 / 256, 118 / 256, 210 / 256), (172 / 256, 6 / 256, 188 / 256), (237 / 256, 121 / 256, 213 / 256)])

fig, ax = plt.subplots(2, gridspec_kw={'height_ratios': [1, 3]})

for ax, dt in zip(ax, [sleep_data, sleep_data_detail]):
	psm = ax.imshow(dt,
		cmap=cmap,
		rasterized=True,
		extent=mdates.date2num([
			date_range[0],
			date_range[1],
			datetime(hour=23, day=1, month=1, year=1970),
			datetime(hour=0, day=1, month=1, year=1970)]),
		aspect='auto'
	)
	fig.colorbar(psm, ax=ax)
	ax.xaxis_date()
	ax.yaxis_date()
	date_format = mdates.DateFormatter('%H:%M:%S')
	ax.yaxis.set_major_formatter(date_format)
fig.autofmt_xdate()
fig.tight_layout()
plt.show()