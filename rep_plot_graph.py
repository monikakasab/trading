import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time
import os
from pathlib import Path

time.sleep(2)
# directory = Path('E:\\Trading\\')
directory = Path(os.getcwd())
prefix = 'PCR_DATA'

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
