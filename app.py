from scipy.interpolate import interp1d
from scipy.interpolate import spline
import plotly.graph_objs as go
import csv
import os
import pandas as pd
import numpy as np
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

app = dash.Dash(__name__)
server = app.server

# Custom Script for Heroku
if 'DYNO' in os.environ:
    app.scripts.append_script({
        'external_url': 'https://cdn.rawgit.com/chriddyp/ca0d8f02a1659981a0ea7f013a378bbd/raw/e79f3f789517deec58f41251f7dbb6bee72c44ab/plotly_ga.js'
    })


app.layout = html.Div([
    # Banner display
    html.Div([
        html.H2(
            'App Name',
            id='title'
        ),
        html.Img(
            src="https://s3-us-west-1.amazonaws.com/plotly-tutorials/logo/new-branding/dash-logo-by-plotly-stripe-inverted.png"
        )
    ],
        className="banner"
    ),

    # Body
    html.Div([
        dcc.Interval(
            id="interval-component",
            interval=1000,
            n_intervals=0
        ),

        dcc.Graph(
            id="accuracy-curve"
        ),




    ],
        className="container",
    )

])


def smooth(scalars, weight=0.6):  # Weight between 0 and 1
    last = scalars[0]  # First value in the plot (first timestep)
    smoothed = list()
    for point in scalars:
        smoothed_val = last * weight + (1 - weight) * point  # Calculate smoothed value
        smoothed.append(smoothed_val)                        # Save it
        last = smoothed_val                                  # Anchor the last smoothed value

    return smoothed

@app.server.before_first_request
def load_csv():
    global csv_reader, step, train_error, val_error

    csvfile = open('eggs.csv', 'r', newline='')
    csv_reader = csv.reader(csvfile, delimiter=',')
    step = []
    train_error = []
    val_error = []




@app.callback(Output('accuracy-curve', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_accuracy_curve(n_intervals):

    if n_intervals > 0:
        layout = go.Layout(
            title="Model Accuracy",
            margin=go.Margin(l=50, r=50, b=50, t=50)
        )

        for row in csv_reader:
            step.append(int(row[0]))
            train_error.append(float(row[1]))
            val_error.append(float(row[2]))

        trace_train = go.Scatter(
            x=step,
            y=train_error,
            mode='lines',
            name='Training'
        )

        trace_val = go.Scatter(
            x=step,
            y=smooth(val_error, 0.7),
            mode='lines',
            name='Validation'
        )

        return go.Figure(
            data=[trace_train, trace_val],
            layout=layout
        )

    return go.Figure(go.Scatter(visible=False))


external_css = [
    "https://cdnjs.cloudflare.com/ajax/libs/normalize/7.0.0/normalize.min.css",  # Normalize the CSS
    "https://fonts.googleapis.com/css?family=Open+Sans|Roboto"  # Fonts
    "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css",
    "https://rawgit.com/xhlulu/0acba79000a3fd1e6f552ed82edb8a64/raw/dash_template.css"
]

for css in external_css:
    app.css.append_css({"external_url": css})

# Running the server
if __name__ == '__main__':
    app.run_server(debug=True)