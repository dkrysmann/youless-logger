import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from helpers.data_processing import load_data
from helpers.charts import (
    dashboard_summary_numbers,
    plot_last_24_hours,
    plot_last_30_days,
    plot_last_year
)


def serve_layout():
    data = load_data()
    return html.Div(children=[
        html.H1(children='Youless energy usage monitoring'),
        dashboard_summary_numbers(data),
        dcc.Graph(
            id='last-24-hours',
            figure=plot_last_24_hours(data['hour'])
        ),
        dcc.Graph(
            id='last-30-days',
            figure=plot_last_30_days(data['day'])
        ),
        dcc.Graph(
            id='last-365-days',
            figure=plot_last_year(data['month'])
        )
        
    ])

       
app = dash.Dash(external_stylesheets=[dbc.themes.FLATLY])

app.title = 'Energy usage monitoring'
app.layout = serve_layout

if __name__ == '__main__':
    app.run_server(debug=True)