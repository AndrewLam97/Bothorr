import os
from datetime import datetime

import plotly.graph_objects as go


#Create local plot of recent historic prices
def plot_historic(recentHistoric):
    orderedHistoric = sorted(recentHistoric.items(), key = lambda x:datetime.strptime(x[0], '%Y-%m-%d'))

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x = [x[0] for x in orderedHistoric],
            y = [y[1] for y in orderedHistoric]
        )
    )
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Value",
        margin=go.layout.Margin(
            l=25, #left margin
            r=0, #right margin
            b=25, #bottom margin
            t=0, #top margin
        )
    )

    if not os.path.exists("images"):
        os.mkdir("images")

    fig.write_image("images/plot_lookup_historic.png")