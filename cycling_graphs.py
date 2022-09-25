from garmindb import ConfigManager

from garmindb.import_monitoring import SleepActivityLevels, RemSleepActivityLevels
from garmindb.garmindb import GarminDb, ActivityRecords, ActivityLaps, CycleActivities, DailySummary, ActivitiesDb, Activities, SleepEvents, Sleep

from datetime import datetime, timedelta, time

import pytz
from typing import *
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import pandas as pd

import math

tz = pytz.timezone('Europe/Berlin')

gDB = ActivitiesDb(ConfigManager.get_db_params(), 0)

events = CycleActivities.get_all(gDB)

full_df = pd.DataFrame()


with gDB.managed_session() as session:
	for ev in events[0:5000]:
		ev_query = session.query(
				ActivityRecords.activity_id,
				ActivityRecords.timestamp,
				ActivityRecords.position_lat,
				ActivityRecords.position_long,
				ActivityRecords.distance,
				ActivityRecords.speed,
				ActivityRecords.hr,
			).filter(ActivityRecords.activity_id==ev.activity_id)

		last = ev_query.order_by(ActivityRecords.record.desc()).first()

		# Filter out by length to get similar ones
		if last is None:
			continue

		if last[4] <= 62 or last[4] >= 69:
			continue

		df = pd.read_sql(ev_query.statement, session.bind)

		df["timestamp"] = df["timestamp"] - df["timestamp"][0]

		laps = session.query(ActivityLaps).filter(ActivityLaps.activity_id==ev.activity_id).all()
		if laps:
			print(df)
			for lap in laps:
				print(f"{lap.distance} {lap.avg_speed} pos: {lap.start_lat} {lap.start_long}")
			full_df = pd.concat([full_df, df])
t_df = full_df.set_index('timestamp')
t_df.groupby('activity_id')["distance"].plot(alpha=0.4)
plt.tight_layout()
plt.figure()
# s_df = full_df.set_index('distance')
# s = (s_df.index.to_series() / 5).astype(int)
# print(s)
# s_df.groupby('activity_id', s).std().set_index(s.index[4::5])
# s_df.groupby('activity_id')["speed"].plot()
full_df["speed"].plot.kde()
plt.xlim(0, 60)
plt.ylim(0, None)
plt.figure()
full_df.groupby('activity_id')["speed"].plot.kde(alpha=0.4)
plt.xlim(0, 60)
plt.tight_layout()
plt.figure()
t_df = full_df.set_index('distance')
t_df.groupby('activity_id')["speed"].plot(alpha=0.2)
plt.tight_layout()
plt.figure()
t_df.groupby('activity_id')["hr"].plot(alpha=0.2)
plt.tight_layout()
plt.show()