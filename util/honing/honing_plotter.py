import os

import plotly.graph_objects as go


#Create local plot of historical cumulative honing deviation from mean
def plot_honing_historic(ordered_honings):        

    layout = go.Layout(
        autosize = False,
        width= 1600,
        height = 1000
    )
    fig = go.Figure(layout=layout)

    fig.add_trace(
        go.Bar(
            name = "Individual",
            x = list(ordered_honings.keys()),
            y = list(l[0] for l in ordered_honings.values())
        )
    )
    fig.add_trace(
        go.Scatter(
            name = "Cumulative",
            x = list(ordered_honings.keys()),
            y = list(l[1] for l in ordered_honings.values())
        )
    )
    fig.update_layout(
        title={
            'text' : "Historical Honing Deviation from Mean",
            'y':0.95,
            'x':0.5,
            'xanchor' : 'center',
            'yanchor' : 'top'
            },

        xaxis_title="Number of Hones",
        yaxis_title="Gold Value"
    )

    if not os.path.exists("images"):
        os.mkdir("images")

    fig.write_image("images/plot_honing_historic.png")
