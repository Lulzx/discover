from utils import load_messages
import datetime
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pandas.plotting import register_matplotlib_converters

messages = load_messages()

timestamps = [message['date'] for message in messages]

datetimes = pd.to_datetime(timestamps, errors='coerce')

df = pd.DataFrame(datetimes, columns=['datetime'])

df['year'] = df['datetime'].dt.year
df['month'] = df['datetime'].dt.month
df['week'] = df['datetime'].dt.isocalendar().week
df['day'] = df['datetime'].dt.day
df['hour'] = df['datetime'].dt.hour
df['minute'] = df['datetime'].dt.minute


hourly_counts = df['hour'].value_counts().sort_index()
sns.barplot(x=hourly_counts.index, y=hourly_counts.values)
plt.title('Hourly Frequency')
plt.show()


# Sort timestamps to ensure they are in chronological order
df.sort_values(by='datetime', inplace=True)

sleep_starts = []
wake_ups = []

# Identify sleep start (last timestamp after midnight) and wake-up (first timestamp in the morning)
for date, group in df.groupby(df['datetime'].dt.date):
    # Assuming sleep starts after 6pm (18:00) and before 4am (04:00)
    sleep_start_candidates = group[(group['datetime'].dt.hour >= 18) | (group['datetime'].dt.hour < 4)]
    # Assuming wake-up times are between 4am (04:00) and 12pm (noon)
    wake_up_candidates = group[(group['datetime'].dt.hour >= 4) & (group['datetime'].dt.hour < 12)]

    if not sleep_start_candidates.empty and not wake_up_candidates.empty:
        # Get the last sleep start timestamp
        sleep_start = sleep_start_candidates['datetime'].iloc[-1]
        # Get the first wake-up timestamp
        wake_up = wake_up_candidates['datetime'].iloc[0]

        # Check if the sleep start is before the wake-up timestamp
        if sleep_start < wake_up:
            sleep_starts.append(sleep_start)
            wake_ups.append(wake_up)

sleep_data = pd.DataFrame({'sleep_start': sleep_starts, 'wake_up': wake_ups})

sleep_data['sleep_duration'] = sleep_data['wake_up'] - sleep_data['sleep_start']

sleep_data['sleep_duration_hours'] = sleep_data['sleep_duration'].dt.total_seconds() / 3600

# Apply a rolling average (moving average) with a window size of your choice
sleep_data['sleep_duration_MA'] = sleep_data['sleep_duration_hours'].rolling(window=7).mean()

fig, ax = plt.subplots(figsize=(14, 7))

ax.plot(sleep_data['sleep_start'], sleep_data['sleep_duration_MA'], label='7-Day Moving Average', linewidth=2)

ax.scatter(sleep_data['sleep_start'], sleep_data['sleep_duration_hours'], label='Sleep Duration', color='orange', s=50, zorder=5)

# Set x-axis to show only quarterly dates
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=(1, 4, 7, 10)))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

fig.autofmt_xdate()

ax.set_xlabel('Date')
ax.set_ylabel('Sleep Duration (hours)')
ax.set_title('Sleep Duration Over Time')

ax.legend()

ax.grid(True)

plt.tight_layout()
plt.show()
