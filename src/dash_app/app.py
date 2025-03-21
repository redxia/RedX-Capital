import sys
import os
import warnings
from dash import Dash, html, dcc 
# import flask
# import dash_bootstrap_components as dbc
# import dash_auth
# from dash_app.tab_sp500_analysis import tab_sp_analysis, update_graph
from tabs import tab_sp500_analysis 
# from dash_app import tab_sp500_analysis
# import tab_sp500_analysis
warnings.filterwarnings('ignore')

app = Dash(__name__) 

# server = flask.Flask(__name__) 

# server.secret_key = 'super secret key'
# server.config['SESSION_TYPE'] = 'filesystem' # some example falsk session , can be something else

# @server.route("/")
# def home():
#     return "Hello, Flask!"

# load_figure_template('LUX')

# app = Dash(server=server, routes_pathname_prefix="/dash/", external_stylesheets=[dbc.themes.LUX], suppress_callback_exceptions=True )
# auth= dash_auth.BasicAuth(app, {'quant':'clear'})

tabs = [ tab_sp500_analysis.tab_sp_analysis ]
#tabs = [ tab_futures ]

app.layout = html.Div( [dcc.Tabs( tabs ) ] )

tab_sp500_analysis.update_graph


__all__ = [
    'update_graph'
]
#TODO tab that does vix analyiss. the probaility densities.
if __name__ == '__main__':
    app.run_server(debug=True)
    # app.run_server(debug=True)


        # daq.BooleanSwitch(
        #     on=True,
        #     label="2D Scaled",
        #     labelPosition="right",
        #     id="id-2D-scaled",
        #     style={"float": "left", "margin-top": "10px", "margin-left": "18px"},
        # ),
        # html.Label(
        #     "Ticker: ",
        #     style={
        #         "margin-left": "120px",
        #         "margin-right": "0px",
        #         "margin-top": "12px",
        #         "float": "left",
        #         "font-weight": "bold",
        #         "font-size": "18px",
        #     },
        # ),
        # html.Label(
        #     id="id-ticker-info",
        #     style={
        #         "margin-left": "16px",
        #         "margin-right": "0px",
        #         "margin-top": "8px",
        #         "float": "left",
        #         "font-size": "24px",
        #     },
        # ),
        # html.Label(
        #     "Latest Date: ",
        #     style={
        #         "margin-left": "100px",
        #         "margin-right": "0px",
        #         "margin-top": "12px",
        #         "float": "left",
        #         "font-weight": "bold",
        #         "font-size": "18px",
        #     },
        # ),
        # html.Label(
        #     id="id-date-info",
        #     style={
        #         "margin-left": "16px",
        #         "margin-right": "0px",
        #         "margin-top": "8px",
        #         "float": "left",
        #         "font-size": "24px",
        #     },
        # ),
        # html.Label(
        #     "E-Garch Latest (Scaled): ",
        #     style={
        #         "margin-left": "100px",
        #         "margin-right": "0px",
        #         "margin-top": "12px",
        #         "float": "left",
        #         "font-weight": "bold",
        #         "font-size": "18px",
        #     },
        # ),
        # html.Label(
        #     id="id-last_egarch-info",
        #     style={
        #         "margin-left": "16px",
        #         "margin-right": "0px",
        #         "margin-top": "8px",
        #         "float": "left",
        #         "font-size": "24px",
        #     },
        # ),
        # html.Div(style={"clear": "both"}),
        # html.Label(
        #     [
        #         "Next Day Shock:",
        #         dcc.Slider(
        #             id="id-return-slider",
        #             min=df["RETURNS"].min(),
        #             max=df["RETURNS"].max(),
        #             step=0.01,
        #             value=-0.1,  # Default value
        #             marks={
        #                 i / 10: f"{i*100 / 10:.1f}" + "%" for i in range(-10, 10, 1)
        #             },
        #         ),
        #         html.Label(
        #             "Current Shock: ", style={"font-weight": "bold", "float": "left"}
        #         ),
        #         # marks={},
        #         html.Label(id="return-slider-output", style={"margin-left": "16px"}),
        #         html.Label(
        #             "E-Garch Shock (Scaled): ",
        #             style={
        #                 "margin-left": "100px",
        #                 "font-weight": "bold",
        #                 "font-size": "14px",
        #             },
        #         ),
        #         html.Label(
        #             id="id-egarch_shock-info",
        #             style={
        #                 "margin-left": "16px",
        #                 "font-weight": "bold",
        #                 "font-size": "18px",
        #             },
        #         ),
        #     ],
        #     style={"width": "25%", "margin-left": "100px"},
        # ),  # , 'margin': 'auto'