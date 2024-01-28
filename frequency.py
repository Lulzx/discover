from utils import load_messages
import datetime
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

messages = load_messages()

timestamps = [int(message['date_unixtime']) for message in messages]

datetimes = pd.to_datetime(timestamps, unit='s')

df = pd.DataFrame(datetimes, columns=['datetime'])

df['day_of_week'] = df['datetime'].dt.dayofweek
df['hour'] = df['datetime'].dt.hour

frequency = df.groupby(['day_of_week', 'hour']).size().unstack(fill_value=0)

plt.figure(figsize=(8, 3))
sns.heatmap(frequency, cmap='YlGnBu', linewidths=.5, annot=False)

plt.ylabel('Day of Week')
plt.xlabel('Hour of Day')
plt.title('Posting Frequency Heatmap')

plt.xticks(np.arange(0.5, len(frequency.columns), 1), frequency.columns)
plt.yticks(np.arange(0.5, len(frequency.index), 1), ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])

plt.show()
