import dash_bootstrap_components as dbc
from dash import html, dcc, Dash, Output, Input
from helpers.data_processing import load_data
from helpers.charts import (
    dashboard_summary_numbers,
    plot_last_year,
    plot_current,
    plot_bar_with_avg_line,
)
from config import DEBUG_MODE


def serve_layout():
    data = load_data()
    data_minute = data['hour']
    data_hour = data['hour']
    data_30days = data['day'].head(30)



    return dbc.Container([
        html.H1(children='Youless energy usage monitoring'),
        dashboard_summary_numbers(data),
        html.Br(),
        dbc.Row([
            dbc.Col([
                dbc.Card(dbc.CardBody(
                    dbc.Tabs([
                        dbc.Tab(label='Current', children=[
                            dcc.Graph(
                                id='current',
                                figure=plot_current(data_minute),
                                config={
                                    'displayModeBar': False
                                }
                            ),
                        ]),
                        dbc.Tab(label='24 Hours', children=[
                            dcc.Graph(
                                id='last-24-hours',
                                figure=plot_bar_with_avg_line(
                                    df=data_hour,
                                    title='Energy consumption per hour',
                                    unit='Wh'
                                ),
                                config={
                                    'displayModeBar': False
                                }
                            ),
                        ]),
                        dbc.Tab(label='30 Days', children=[
                            dcc.Graph(
                                id='last-30-days',
                                figure=plot_bar_with_avg_line(
                                    df=data_30days,
                                    title='Energy consumption last 30 days',
                                    unit='kWh'
                                ),
                                config={
                                    'displayModeBar': False
                                }
                            ),
                        ])
                    ])
                )), 
            ])
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col([
                dbc.Card(dbc.CardBody(dcc.Graph(
                    id='last-365-days',
                    figure=plot_last_year(data['month'], title='Energy consumption last 12 months', unit='kWh'),
                    config={
                        'displayModeBar': False
                    }
                )))
            ])
        ])
    ], fluid=True)

       

app = Dash(external_stylesheets=[dbc.themes.FLATLY])

app.title = 'Energy usage monitoring'
app.layout = serve_layout

if __name__ == '__main__':
    app.run_server(debug=DEBUG_MODE, host='0.0.0.0', port='8050')