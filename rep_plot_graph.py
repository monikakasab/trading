import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime, time
from zoneinfo import ZoneInfo
import time as t
import os
from pathlib import Path


def wait_until_9_18_and_run():
                 target_time = time(9, 18, 0)  # 9:18 AM
                 now = datetime.now(tz=ZoneInfo('Asia/Kolkata'))
                 now_naive = now.replace(tzinfo=None)

                 # If current time is after 9:18 AM, run immediately
                 if now_naive.time() >= target_time:
                                  return

                 # Otherwise, wait until 9:18 AM
                 secs_to_wait = (
                     datetime.combine(now_naive.date(), target_time) -
                     now_naive).total_seconds()
                 if secs_to_wait > 0:
                                  print(
                                      f"Waiting for {secs_to_wait} seconds until 9:18 AM..."
                                  )
                                  t.sleep(secs_to_wait)


wait_until_9_18_and_run()
# directory = Path('E:\\Trading\\')s
directory = Path(os.getcwd())
todays_date = datetime.now().strftime('%Y_%m_%d')
prefix = f'PCR_DATA_{todays_date}'

wait_seconds = 2
filename = f"{prefix}.csv"
while not os.path.exists(filename):
                 print(
                     f"{filename} not found. Waiting for {wait_seconds} seconds..."
                 )
                 t.sleep(wait_seconds)

csv_file = next((f.name for f in directory.iterdir()
                 if f.name.startswith(prefix) and f.is_file()), None)
os.chdir(directory)

fig, ax = plt.subplots()
line, = ax.plot([], [], 'b-', marker='o')  # Line object for updating graph


def animate(i):
                 # Read CSV file every frame
                 data = pd.read_csv(csv_file)

                 # Extract columns for x and y (adjust column names as per your file)
                 x = data['TIMESTAMP']  # e.g. timestamps or sequence numbers
                 y = data['PCR']  # values to plot

                 ax.clear()  # Clear previous frame

                 # Optionally format x-axis if time data (parse to datetime if needed)
                 # For simple sequence numbers strings, this can be skipped

                 ax.plot(x, y, 'b-o')
                 ax.set_title('PCR GRAPH')
                 ax.set_xlabel('Time')
                 ax.set_ylabel('PCR')
                 ax.grid(True)
                 plt.xticks(rotation=45)  # Rotate x labels if timestamps

                 plt.tight_layout()


# Create animation, update every 1000 ms (1 second)
ani = FuncAnimation(fig, animate, interval=1000)

plt.show()
