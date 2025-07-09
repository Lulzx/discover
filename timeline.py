import matplotlib.pyplot as plt
import pandas as pd
from utils import load_messages


def plot_timeline(output_path: str = 'images/timeline.png') -> None:
    messages = load_messages()
    if not messages:
        print('No messages found for timeline')
        return
    dates = [msg['date'] for msg in messages if 'date' in msg]
    df = pd.to_datetime(dates, errors='coerce').to_frame(name='datetime')
    df['date'] = df['datetime'].dt.date
    counts = df.groupby('date').size()
    counts.plot(kind='line', figsize=(10, 4))
    plt.ylabel('Messages')
    plt.title('Message Timeline')
    plt.tight_layout()
    plt.savefig(output_path)
    print(f'Saved timeline chart to {output_path}')


if __name__ == '__main__':
    plot_timeline()
