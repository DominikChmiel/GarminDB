import GarminDB
from garmin_db_config_manager import GarminDBConfigManager

from import_garmin import SleepActivityLevels, RemSleepActivityLevels

from datetime import datetime, timedelta, time

import pytz
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

import math

tz = pytz.timezone('Europe/Berlin')

gDB = GarminDB.GarminDB(GarminDBConfigManager.get_db_params(), 0)

sleep_events = GarminDB.SleepEvents.get_all(gDB)

date_range = [sleep_events[0].timestamp + timedelta(days=-1), sleep_events[-1].timestamp + timedelta(days=2)]

days = (date_range[1] - date_range[0]).days

YSTEP = timedelta(minutes=6)
DAILY_Y = int(timedelta(days=1).total_seconds() / YSTEP.total_seconds())

sleep_data = np.array([[0] * days] * DAILY_Y)
sleep_data.fill(-2)


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
	add_sleep_state(sleep_data, sev.start, sev.end, -1.0)

sleep_data_detail = np.array([[0] * days] * DAILY_Y)
sleep_data_detail.fill(-2)
sleep_data_detail = np.copy(sleep_data)

# Augment data with sleep Events
print(sleep_events[0])
for ev in sleep_events:
	slevel = RemSleepActivityLevels[ev.event]
	localized = tz.localize(ev.timestamp)
	if True or slevel.value >= RemSleepActivityLevels.awake.value:
		tofs = timedelta(hours=2)
		if ev.timestamp > datetime(year=2019, month=10, day=27) and ev.timestamp < datetime(year=2020, month=3, day=28):
			tofs -= timedelta(hours=1)
		add_sleep_state(sleep_data_detail, ev.timestamp + tofs, ev.timestamp + tofs + timedelta(hours=ev.duration.hour, minutes=ev.duration.minute), slevel.value)

print(sleep_data.shape)

#print(sleep_events)

# vegetables = ["cucumber", "tomato", "lettuce", "asparagus",
#               "potato", "wheat", "barley"]
# farmers = ["Farmer Joe", "Upland Bros.", "Smith Gardening",
#            "Agrifun", "Organiculture", "BioGoods Ltd.", "Cornylee Corp."]

# harvest = np.array([[0.8, 2.4, 2.5, 3.9, 0.0, 4.0, 0.0],
#                     [2.4, 0.0, 4.0, 1.0, 2.7, 0.0, 0.0],
#                     [1.1, 2.4, 0.8, 4.3, 1.9, 4.4, 0.0],
#                     [0.6, 0.0, 0.3, 0.0, 3.1, 0.0, 0.0],
#                     [0.7, 1.7, 0.6, 2.6, 2.2, 6.2, 0.0],
#                     [1.3, 1.2, 0.0, 0.0, 0.0, 3.2, 5.1],
#                     [0.1, 2.0, 0.0, 1.4, 0.0, 1.9, 6.3]])


fig, ax = plt.subplots(2)
ax[0].imshow(sleep_data)
ax[1].imshow(sleep_data_detail)

y_ticks = []
y_labels = []
for i in range(0, 25, 4):
	y_ticks.append(int(timedelta(hours=i) / YSTEP))
	y_labels.append('{:2d}:00'.format(i))

print(y_ticks, y_labels)

for a in ax:
	a.set_yticks(y_ticks)
	a.set_yticklabels(y_labels)

# # We want to show all ticks...
# ax.set_xticks(np.arange(len(farmers)))
# ax.set_yticks(np.arange(len(vegetables)))
# # ... and label them with the respective list entries
# ax.set_xticklabels(farmers)
# ax.set_yticklabels(vegetables)

# # Rotate the tick labels and set their alignment.
# plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
#          rotation_mode="anchor")

# # Loop over data dimensions and create text annotations.
# for i in range(len(vegetables)):
#     for j in range(len(farmers)):
#         text = ax.text(j, i, harvest[i, j],
#                        ha="center", va="center", color="w")

# ax.set_title("Harvest of local farmers (in tons/year)")
fig.tight_layout()
plt.show()