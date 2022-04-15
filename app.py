import dash_bootstrap_components as dbc
from dash import html, dcc, Dash, Output, Input
from helpers.data_processing import (
    EnergyDataDay, 
    EnergyDataHour,
    EnergyDataMinute, 
    EnergyDataMonth,
    GasDataDay,
    GasDataHour,
    GasDataMonth
)
from helpers.charts import MonitoringLayout
from config import DEBUG_MODE, GAS_ENABLED

nav_items = [dbc.NavLink("Electricity", href="/", active="exact")]
if GAS_ENABLED:
    nav_items.append(
        dbc.NavLink("Gas", href="/gas", active="exact")
    )
nav = dbc.Container([dbc.NavbarSimple(
    children=nav_items,
    brand='Youless Monitor',
    brand_href="#",
    color="primary",
    dark=True,
)])


content = html.Div(id="page-content")  

app = Dash(external_stylesheets=[dbc.themes.FLATLY])
app.title = 'Energy usage monitoring'
app.layout = dbc.Container([dcc.Location(id="url"), nav, html.Br(), content])


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        energy_layout = MonitoringLayout(
            data_minute=EnergyDataMinute,
            data_hour=EnergyDataHour,
            data_day=EnergyDataDay,
            data_month=EnergyDataMonth
        )

        return energy_layout.render(
            title='Energy Monitoring',
            summary_stats_suffix=' kWh',
            last_24h_unit='Wh',
            last_30d_unit='kWh',
            last_year_unit='kWh'
        )
    elif pathname == "/gas":
        gas_layout = MonitoringLayout(
            data_minute=None,
            data_hour=GasDataHour,
            data_day=GasDataDay,
            data_month=GasDataMonth
        )

        return gas_layout.render(
            title='Gas Monitoring',
            summary_stats_suffix=' m³',
            last_24h_unit='L',
            last_30d_unit='m³',
            last_year_unit='m³'
        )
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )

if __name__ == '__main__':
    app.run_server(debug=DEBUG_MODE, host='0.0.0.0', port='8050')