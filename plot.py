import sys
import pandas as pd
import matplotlib.pyplot as plt
from glob import glob

_, in_dir = sys.argv

dates = [x.split('/')[1].split('_')[0] for x in glob(in_dir + '/*')]

dates = pd.to_datetime(dates)
df = pd.DataFrame(dates, columns=['date'])

date_counts = df['date'].value_counts().sort_index()
cumulative_counts = date_counts.cumsum()

plt.figure(figsize=(10, 6))
plt.step(cumulative_counts.index, cumulative_counts, where='post')
plt.xlabel('Date')
plt.ylabel('uploaded contributions (cumulative)')
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()

out_name = in_dir.replace('/', '') + '.pdf'

print(out_name)

plt.savefig(out_name)
plt.clf()
