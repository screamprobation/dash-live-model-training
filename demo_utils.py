import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output, State


def demo_components(demo_mode):
    if demo_mode:
        # Markdown files
        with open('demo.md', 'r') as file:
            demo_md = file.read()

        return [
            ########################## DEMO COMPONENTS BELOW ####################################
            # Hidden Div that will store the result of simulating a model run
            html.Div(id='storage-simulated-run', style={'display': 'none'}),

            # An interval that increments the simulation step count at a fixed time interval
            dcc.Interval(
                id='interval-simulated-step',
                interval=125,  # Updates every 100 milliseconds, i.e. every step takes 25 ms
                n_intervals=0
            ),

            html.Div([
                dcc.Dropdown(
                    id='dropdown-demo-dataset',
                    options=[
                        {'label': 'CIFAR 10', 'value': 'cifar'},
                        {'label': 'MNIST', 'value': 'mnist'},
                        {'label': 'Fashion MNIST', 'value': 'fashion'}
                    ],
                    placeholder="Select a demo dataset",
                    searchable=False,
                    className='five columns',
                ),

                dcc.Dropdown(
                    id='dropdown-simulation-model',
                    options=[
                        {'label': '1-Layer Neural Net', 'value': 'softmax'},
                        {'label': 'Simple Conv Net', 'value': 'cnn'}
                    ],
                    placeholder="Select Model to Simulate",
                    searchable=False,
                    className='five columns',
                )

            ],
                className="row"
            ),

            html.Div(
                dcc.Markdown(demo_md, className='ten columns'),
                style={
                    'margin': '20px'
                },
                className='row'
            )
            ########################## DEMO COMPONENTS ABOVE ####################################
        ]

    else:
        return []


def demo_callbacks(app, demo_mode):
    if demo_mode:
        @app.server.before_first_request
        def load_demo_run_logs():
            global data_dict, demo_md

            names = ['step', 'train accuracy', 'val accuracy', 'train cross entropy', 'val cross entropy']

            data_dict = {
                'softmax': {
                    'cifar': pd.read_csv('demo_run_logs/cifar_softmax_run_log.csv', names=names),
                    'mnist': pd.read_csv('demo_run_logs/mnist_softmax_run_log.csv', names=names),
                    'fashion': pd.read_csv('demo_run_logs/fashion_softmax_run_log.csv', names=names)
                },

                'cnn': {
                    'cifar': pd.read_csv('demo_run_logs/cifar_cnn_run_log.csv', names=names),
                    'mnist': pd.read_csv('demo_run_logs/mnist_cnn_run_log.csv', names=names),
                    'fashion': pd.read_csv('demo_run_logs/fashion_cnn_run_log.csv', names=names)
                }
            }

        @app.callback(Output('storage-simulated-run', 'children'),
                      [Input('interval-simulated-step', 'n_intervals')],
                      [State('dropdown-demo-dataset', 'value'),
                       State('dropdown-simulation-model', 'value')])
        def simulate_run(n_intervals, demo_dataset, simulation_model):
            if simulation_model and demo_dataset and n_intervals > 0:
                step = n_intervals * 5
                run_logs = data_dict[simulation_model][demo_dataset]

                run_below_steps = run_logs[run_logs['step'] <= step]
                json = run_below_steps.to_json(orient='split')

                return json

        @app.callback(Output('interval-simulated-step', 'n_intervals'),
                      [Input('dropdown-demo-dataset', 'value'),
                       Input('dropdown-simulation-model', 'value')])
        def reset_interval_simulated_step(*_):
            return 0

        @app.callback(Output('run-log-storage', 'children'),
                      [Input('interval-log-update', 'n_intervals')],
                      [State('storage-simulated-run', 'children')])
        def get_run_log(_, simulated_run):
            if simulate_run:
                return simulated_run
