import matplotlib.pyplot as plt
import os
from datetime import datetime
import itertools

#Create local plot of recent historic prices
def plot_historic(recentHistoric):
    orderedHistoric = sorted(recentHistoric.items(), key = lambda x:datetime.strptime(x[0], '%Y-%m-%d'))

    xAxis = [x[0] for x in orderedHistoric]
    yAxis = [y[1] for y in orderedHistoric]
    plt.grid(True)

    #Line Graph
    plt.figure(figsize=(10, 6), dpi=80)
    plt.plot(xAxis, yAxis, color='blue', marker='o')
    plt.xlabel('Date')
    plt.ylabel('Value')

    if os.path.exists("plot.png"):
        os.remove("plot.png")
    plt.savefig('plot.png', bbox_inches='tight')