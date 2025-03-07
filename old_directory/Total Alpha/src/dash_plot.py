from dash import Dash, html, dcc, callback, Output, Input, ctx, State
import plotly.express as px
import pandas as pd 
import sys
import os
import plotly.graph_objs as go
import plotly.io as pio
import numpy as np
import math
from plotly.subplots import make_subplots
from scipy.interpolate import splrep, splev
import datetime

app = Dash(__name__)

optimal_weights=pd.DataFrame()
total_index=pd.DataFrame()
correlation=pd.DataFrame()


# Cache={}
# Cache['Tickers'] = optimal_weights['Tickers']
# Cache['ref_dates'] = get_dates_from_qt_db( ticker =Cache['tickers'][0] , data_source = 'BBG', ascending = False )

from dash import Dash, dcc, html, Output, Input, State      # pip install dash
import plotly.express as px


app = Dash(__name__)
app.layout = html.Div([
    dcc.Tabs([
        dcc.Tab(label='Tab 1', children=[
            html.H1("Markowitz Universe", style={'textAlign': 'center'}),
            dcc.Graph(id='line-history', figure={}),
        ]),
        dcc.Tab(label='Tab 2', children=[
            html.H1("Stock Universe", style={'textAlign': 'center'}),
        ]),
        dcc.Tab(label='Tab 3', children=[
            html.H1("Correlation Matrix", style={'textAlign': 'center'}),
        ]),
    ])
    
    dcc.Dropdown(id='ticker-name', options=, value='TSLA', clearable=False, style={'width': '50%'}),
    html.Div(id='price-placeholder', children=[]),
    dcc.Graph(id='line-history', figure={}),
    html.Hr(),
    dcc.Input(id='alert-value', type='number', min=0, max=1000, value=0),
])


@app.callback(
    Output('line-history', 'figure'),
    Output('price-placeholder', 'children'),
    Input('trigger', 'n_intervals'),
    Input('ticker-name', 'value'),
)
def display_price(_, ticker_name, alert_permission, alert_value):
    fmp = FMP(output_format='pandas', api_key='YourFMPdeveloperAPIkey')                          # <-- Update here-------------------
    stock = fmp.get_quote_short(ticker_name)
    stock_history = fmp.get_historical_chart('1hour', ticker_name)
    current_time = datetime.now().strftime("%H:%M:%S")

    if alert_permission == 'Yes, phone alerts':
        if stock.price[0] >= alert_value:
            send_alert('Alert: Buy Stock',
                        f'{ticker_name} passed your alert threshold of ${alert_value} '
                        f'and is now at ${stock.price[0]} per share.',
                        '3475140963@vtext.com')                                                  # <-- Update here-------------------

    elif alert_permission == 'Yes, email alerts':
        if stock.price[0] >= alert_value:
            send_alert('Alert: Buy Stock',
                        f'{ticker_name} passed your alert threshold of ${alert_value} '
                        f'and is now at ${stock.price[0]} per share.',
                        'EmailToAddress@gmail.com')                                              # <-- Update here-------------------

    history_fig = px.line(stock_history, x='date', y='high')
    return history_fig, html.Pre(f"Time: {current_time}\nPrice: ${stock.price[0]}")


if __name__ == '__main__':
    app.run()





# app.layout = dbc.Container([
#     html.Div(
#         # className='bg-primary',
#         style={'display': 'flex', 'height': '100vh', 'background-color': '#2e21de'},
#         children=[
#             html.Div(
#                 className='sidebar',
#                 children=[
#                     html.Img(src='/assets/CS-Logo-Blueberry.png', style={'width': '128px', 'height': 'auto', 'display':'inline-block'}),
#                     html.Div(className='side-menu-h1',
#                              children=[html.Span("\u03C3", className='sigma'),
#                                        html.Span('Clear Street Risk', className='side-menu-h1'),
#                                        html.Div(className='dashed-line')
#                     ]),
                    
#                     dcc.Link('Volatility Analysis', href='/volatility', className='menu-option')] 
#                 ),
#         html.Div(
#             className='main-content-bg',
#             children=[dcc.Location(id='url', refresh=False), 
#                       html.Div(id='page-content')])
# ])])

# @callback(
#     Output('page-content', 'children'),
#     [Input('url', 'pathname')]
# )
# def display_page(pathname):
#     if pathname == '/volatility':
#         return html.Div(
#             className='volatility',
#             children=[
#                 html.H1('Implied Volatility', style={'font-size':'14px'}),
#                 html.Label( "Tickers: ", className='select-name'),
#                 dcc.Dropdown(Cache['tickers'], Cache['tickers'][0], id='ticker-selection', className='select-fields'),
                
#         # style={'margin-left': '6px', 'margin-right': '10px','margin-top': '3px', 'width': '120px', "float": "left", 'font-size': '14px', 'color':'black'}
#                 html.Label( "Date (As Of)", className='select-name'),
#                 dcc.Dropdown(Cache['ref_dates'], Cache['ref_dates'][0], id='ref_date-selection', className='select-fields', style={'width':'132px','float':'left'} ), #style={'margin-left':'6px','width': '160px', "float": "left", 'color':'white'}
#                 html.Label( "Model: ", className='select-name',style={'margin-right':'15px','margin-left':'24px'}), #style={'margin-left':'60px', 'margin-right':'0px','margin-top':'5px', "float": "left",  "font-weight": "bold", 'text-align':'right', 'color':'white'}
#                 html.Label( id="id-fitting-model-info", style={'margin-left':'15px', 'margin-right':'0px','margin-top':'5px', "float": "left",'text-transform': 'capitalize', 'color':'white'}),
#                 html.Label("Expiry: ", className='select-name'),  #style={'margin-left':'15px', 'margin-right':'0px','margin-top':'15px', "float": "left",  "font-weight": "bold"}
#                 dcc.Dropdown(
#                     options=[],
#                     value=[],
#                     id ='term-checklist',
#                     multi=True,
#                     className='select-fields', style={'width':'512px','float':'left'}), # style={'margin-left':'15px', 'margin-right':'15px', 'margin-top':'15px', "float": "left", 'color':'white'}
#                 html.Label(id='selected-dates', style={'margin-top': '20px', 'color': 'white'}), # Todo need to see how this works.
#                 html.Div(style = {'clear': "both"}),
#                 html.Label( "Strike: ", className='select-name',style={'margin-top':'32px'}), #style={'margin-left':'15px', 'margin-right':'0px','margin-top':'15px', "float": "left", "font-weight": "bold"} 
#                 dcc.Dropdown(['Strike', 'Log(Strike/Spot)', 'Norm Strike'], 'log(K/S)', id = "xaxis_type", className='select-fields', style={'margin-top':'8px', 'width':'148px', 'float':'left'} ), # , inline=True # style={'margin-left':'15px', 'margin-right':'0px','margin-top':'15px', "float": "left"}
#                 html.Label( "Volatility: ", className='select-name',style={'margin-top':'32px','float':'left'}), #style={'margin-left':'15px', 'margin-right':'0px','margin-top':'15px', "float": "left",  "font-weight": "bold"} 
#                 dcc.RadioItems(['Implied Volatility', 'Variance'], 'Implied Volatility', id = "yaxis_type", inline=True, className='select-fields',style={'color':'white','margin-top':'18px','font-size':'10px'}),#style={'margin-left':'15px', 'margin-right':'0px','margin-top':'15px', "float": "left"}
#                 daq.BooleanSwitch(
#                     on=True,
#                     label="Display - Bid-Ask",
#                     labelPosition="left",
#                     id="id-show-error-bars",
#                     style={"float": "left",'margin-top':'18px','margin-left':'15px', 'font-size':'10px'}
#                 ),
#                 html.Button('Reset', id='reset-button', n_clicks=0, style={'margin-top':'24px', 'float':'left','margin-left':'15px'}),
#                 html.Div( style = {'clear': "both"}  ),
#                 html.Div(style={'display': 'flex', 'flexWrap': 'wrap', 'height':'600px'},
#                          children = [dcc.Graph(id='graph-content', style = {'box-shadow': "0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)", 'width':'50%','margin-top':'15px'},figure={'layout':{'title':'Volatility Skew','paper_bgcolor':'black','plot_bgcolor':'#808080','font':{'color':'white'},'gridcolor':'#cfcfcf' }}), #, 'margin-left':'15px', 'margin-top':'15px', 'margin-bottom':'15px','margin-right':'15px'
#                                       dcc.Graph(id='graph-content-3d', style = {'box-shadow': "0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)",'width':'50%', 'margin-top':'15px'},figure={'layout':{'title':'Volatility Surface','plot_bgcolor':'#808080','paper_bgcolor':'black','font':{'color':'white'}, 'gridcolor':'#cfcfcf'}})  #, 'margin-left':'15px', 'margin-top':'15px', 'margin-right':'15px'
#                                     ] 
#                         ),
#                 # html.Div( children = [  ]  ),
#                 html.Br(),
#                 html.Div(style={'display': 'flex', 'flexWrap': 'wrap', 'height':'600px'},
#                          children = [dcc.Graph(id='graph-content-price', 
#                                                style = {'box-shadow': "0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)", 'width':'50%'}, 
#                                                figure={'layout':{'title':'P/C OTM Prices','plot_bgcolor':'#808080','paper_bgcolor':'black','font':{'color':'white'}, 'gridcolor':'#cfcfcf'}})  
#                                       ]),        #, 'margin-left':'15px', 'margin-top':'15px', 'margin-bottom':'15px','margin-right':'15px' # , style = {'box-shadow': "0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)", 'width':'50%'}
                

#                 html.Label( "explore fit: ", style={'margin-left':'15px', 'margin-right':'0px','margin-top':'15px', "float": "left",  "font-weight": "bold"} ),
#                 daq.BooleanSwitch(
#                     on=False,
#                     label="",
#                     labelPosition="left",
#                     id="adjust_fit",
#                     style={"float": "left",'margin-top':'10px','margin-left':'15px'}),
#                 html.Div( style = {'clear': "both"}  ),
#                 html.Div( hidden = True, id="id-adjust-fit-elements", 
#                           children=[
#                         html.Div( style = {'clear': "both"}  ),
#                         html.Label( "explore num params", style={'margin-left':'15px', 'margin-right':'0px', 'margin-top':'15px', "float": "left",  "font-weight": "bold"} ),
#                         dcc.Dropdown([4,5,6,7,8,9,10], 4, id='id-explore-num-params',  style={'margin-left':'5px', 'width': '120px', "float": "left"} ),
#                         html.Label( "explore term: ", style={'margin-left':'15px', 'margin-right':'0px','margin-top':'15px', "float": "left",  "font-weight": "bold"} ),
#                         dcc.RadioItems( [], '', id = "id-term-adjust", inline=True,  style={'margin-left':'15px', 'margin-right':'0px','margin-top':'15px', "float": "left"}),
#                         html.Div( style = {'clear': "both"}  ),
#                         html.Div(children = [  
#                             html.Label( "param mults: ", style={'margin-left':'15px', 'margin-right':'0px','margin-top':'15px', 'margin-bottom':'15px', "font-weight": "bold", "float": "left"} ),
#                             html.Label( "", id="id-show_edit_term", style={'margin-left':'15px', 'margin-right':'0px','margin-top':'15px', 'margin-bottom':'15px',  "float": "left"} ),
#                             html.Div( style = {'clear': "both"}  ),
#                             dcc.Slider(0.5, 2, 0.01, value=1, marks=None, id='id-param-a1',  tooltip={"placement": "right", "always_visible": True}),
#                             dcc.Slider(0.5, 2, 0.01, value=1, marks=None, id='id-param-b1', tooltip={"placement": "right", "always_visible": True}),
#                             dcc.Slider(0.5, 2, 0.01, value=1, marks=None, id='id-param-a2', tooltip={"placement": "right", "always_visible": True}),
#                             dcc.Slider(0.5, 2, 0.01, value=1, marks=None, id='id-param-b2', tooltip={"placement": "right", "always_visible": True}),
#                             #dcc.Slider(0.5, 2, 0.01, value=1, marks=None, id='id-param-c', tooltip={"placement": "right", "always_visible": True}),
#                             html.Div( style = {'clear': "both"}  ),
#                             html.Label( "params: ", style={'margin-left':'15px', 'margin-right':'0px','margin-top':'15px', 'margin-bottom':'15px', "font-weight": "bold", "float": "left"} ),
#                             html.Label( "", id="id-params", style={'margin-left':'15px', 'margin-right':'0px','margin-top':'15px', 'margin-bottom':'0px',  "float": "left"} ),
#                             html.Div( style = {'clear': "both"}  ),
#                             html.Label( "fit residual: ", style={'margin-left':'15px', 'margin-right':'0px','margin-top':'0px', 'margin-bottom':'15px', "font-weight": "bold", "float": "left"} ),
#                             html.Label( "", id="id-objective", style={'margin-left':'15px', 'margin-right':'0px','margin-top':'0px', 'margin-bottom':'15px',  "float": "left"} ),
#                             html.Div( style = {'clear': "both"}  ),
#                     ], hidden = True, id="id-slider_div", style = { 'width': '500px','box-shadow': "0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)", 'margin-left':'15px', 'margin-top':'15px', 'margin-bottom':'15px','margin-right':'15px', "float": "left"} ),
                
#                     html.Div( children = [], id="id-res-figs", style = {'box-shadow': "0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)", 'margin-left':'15px', 'margin-top':'15px', 'margin-bottom':'15px','margin-right':'15px', "float": "left"}),
#                     html.Div(children = [
#                         html.Label( "Spline: ", style={'margin-left':'15px', 'margin-right':'0px','margin-top':'15px', 'margin-bottom':'15px', "font-weight": "bold", "float": "left"} ),
#                         html.Div( style = {'clear': "both"}  ),
#                         html.Label( "tension: ", style={'margin-left':'15px', 'margin-right':'0px','margin-top':'15px', 'margin-bottom':'15px', "font-weight": "bold", "float": "left"} ),
#                         dcc.Input( id="id-spline_tension", type="number", debounce=True, placeholder="spline tension" , style={'margin-left':'15px', 'margin-right':'15px','margin-top':'15px', 'margin-bottom':'15px', "font-weight": "bold", "float": "left", "width": '120px'}),
#                         html.Div( style = {'clear': "both"}  ),
#                         html.Div( children = [], id="id-spline-figs" , style={'margin-left':'15px', 'margin-right':'0px','margin-top':'15px', 'margin-bottom':'15px', "font-weight": "bold", "float": "left"} ),
#                     ], hidden = True, id="id-spline-box", style = {'box-shadow': "0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)", 'margin-left':'15px', 'margin-top':'15px', 'margin-bottom':'15px','margin-right':'15px', "float": "left"} ),
#                     html.Div( style = {'clear': "both"}  ),
#                 ])
#                 ,

#         html.Div( style = {'clear': "both"})
#         ],
#         )
#     else:
#         return html.Div(
#             style={'display': 'flex',  # Use flexbox to center the content
#                                    'justify-content': 'center',  # Center horizontally
#                                    'align-items': 'center',  # Center vertically
#                                    'height': '50vh',
#                                    'width': '50vw',},
#             children=[           
#             html.H4("", style={'color': 'white'})]
#         )



# @callback(
#     Output('ref_date-selection', 'options'),
#     Output('ref_date-selection', 'value'),
#     Output('term-checklist', 'options'),
#     Output("id-term-adjust", 'options'),

#     Input('ticker-selection', 'value'),
#     Input('ref_date-selection', 'value'),
#     #Input('id-num-params', 'value'),
# )
# def update_ticker_info(ticker, ref_date ):

#     num_params = 4

#     if ctx.triggered_id in [ 'ref_date-selection', 'id-num-params' ]:
#         raise PreventUpdate 

#     terms =[]
#     key= f"dates::{ticker}"
#     if key not in Cache:
#         Cache[key] = get_dates_from_qt_db( ticker = ticker, data_source = 'BBG', ascending = False )
#     else:
#         if ref_date in Cache[key]:
#             raise PreventUpdate 

#     if ref_date in Cache[key]:
#         new_ref_date = ref_date
#     else:
#         if len(Cache[key])>0:
#             new_ref_date = Cache[key][0]
#         else:        
#             new_ref_date =''

#     data_key = f"{ticker}:{new_ref_date}:{num_params}"
#     if data_key not in Cache:
#         try:
#             btc_options, btc_market,  param_matrix, m, iv_ssvi = do_fit_and_plots( ticker, model = model, ref_date = new_ref_date, num_params = num_params, num_strike_points = num_strike_points, pricing_model=pricing_model, use_borrow_from_db =use_borrow_from_db  )
#             Cache[ data_key ] = {"btc_options":btc_options, "btc_market":btc_market,  "param_matrix":param_matrix, "m":m, "iv_ssvi":iv_ssvi}
#             terms= list(np.unique(btc_market['expiration_date']))
#             terms.sort()
#         except Exception as e:
#             Cache[ data_key ] = None    
#             print(e)
#             raise PreventUpdate
#     else:    
#         terms= list(np.unique(Cache[ data_key ]["btc_market"]['expiration_date']))

#     return Cache[key], new_ref_date, terms, terms 

# @callback(
#     Output('term-checklist', 'options', allow_duplicate=True),
#     Output("id-term-adjust", 'options', allow_duplicate=True),
    
    

#     Input('ticker-selection', 'value'),
#     Input('ref_date-selection', 'value'),
#     #Input('id-num-params', 'value'),
#     prevent_initial_call=True
# )
# def update_terms(ticker, ref_date ):
#     num_params = 4

#     if ctx.triggered_id == 'ticker-selection':
#         raise PreventUpdate 

#     data_key = f"{ticker}:{ref_date}:{num_params}"
#     if data_key not in Cache:
#         try:
#             btc_options, btc_market,  param_matrix, m, iv_ssvi = do_fit_and_plots( ticker, model = model, ref_date = ref_date , num_params = num_params, num_strike_points = num_strike_points , pricing_model=pricing_model, use_borrow_from_db =use_borrow_from_db)
#             Cache[ data_key ] = {"btc_options":btc_options, "btc_market":btc_market,  "param_matrix":param_matrix, "m":m, "iv_ssvi":iv_ssvi}
#             terms= list(np.unique(btc_market['expiration_date']))
#             terms.sort()
#             return terms, terms
#         except:
#             Cache[ data_key ] = None   
#             return [],[]  
#     else:
#         if Cache[ data_key ] is None:
#             return [],[]
#         else:
#             btc_market = Cache[ data_key ]["btc_market"]
#             terms= list(np.unique(btc_market['expiration_date']))
#             terms.sort()
#             return terms, terms


# @callback(
#     Output('graph-content', 'figure'),
#     Output('graph-content-price', 'figure'),
#     Output('graph-content-3d', 'figure'),
#     Output('id-adjust-fit-elements', 'hidden'),
#     Output("id-params", 'children'),
#     Output("id-show_edit_term", 'children'),
#     Output("id-objective", 'children'),
#     Output("id-res-figs", 'children'),
#     Output("id-slider_div", 'hidden'),
#     Output("id-spline-figs", 'children'),
#     Output("id-spline-box", 'hidden'),
#     Output("id-fitting-model-info", 'children'),

#     Input('ticker-selection', 'value'),
#     Input('ref_date-selection', 'value'),
#     Input('term-checklist', 'value'),
#     Input("xaxis_type", 'value'),
#     Input("yaxis_type", 'value'),
#     Input("adjust_fit", 'on'),
#     Input("id-term-adjust", 'value'),
#     Input('id-param-a1', 'value'),
#     Input('id-param-b1', 'value'),
#     Input('id-param-a2', 'value'),
#     Input('id-param-b2', 'value'),
#     #Input('id-num-params', 'value'),
#     Input('id-explore-num-params', 'value'),
#     Input("id-show-error-bars", 'on'),
#     Input('id-spline_tension', 'value'),
    
# )
# def update_graph(ticker, ref_date1, selected_terms, xaxis_type, yaxis_type, adjust_fit, adjust_term, mult_param_a1, mult_param_b1, mult_param_a2, mult_param_b2, explore_num_params, show_error_bars, adjust_spline_tension ):
#     #dff = df[df.country==value]
#     num_params = 4

#     print("adjust_fit ",adjust_fit)

#     model_data = get_fit_model_by_ticker( ticker )

#     fitting_model_info = f" JW {num_params}"
#     if (model_data is not None) and (len(model_data) >0):    
#         fitting_model_info = f"{model_data['MODEL'].iloc[0]} {model_data['MODEL_PARAM'].iloc[0]}"

#     """
#     cfg ={}
#     model_data= None
#     if fit_model_setting is not None:
#         model_data= fit_model_setting[ fit_model_setting['TERM'] == null_date ]
#         cfg['MODEL'] = model_data['MODEL'].iloc[0]
#         cfg['MODEL_PARAM'] = model_data['MODEL_PARAM'].iloc[0]
#     """
#     ticker_info_key= f"dates::{ticker}"
#     if ticker_info_key not in Cache: # ticker info is not updated yet, ref_date might be stale and not present for this symbol
#         raise PreventUpdate
    
#     text_status= ""
#     objective_str = ""
#     res_figs =[]
#     spline_figs =[]
#     key= f"{ticker}:{ref_date1}:{num_params}"
#     if key not in Cache:
#         try:
#             btc_options, btc_market,  param_matrix, m, iv_ssvi = do_fit_and_plots( ticker, model = model, ref_date = ref_date1, num_params=num_params, num_strike_points = num_strike_points, pricing_model=pricing_model, use_borrow_from_db =use_borrow_from_db )
#             Cache[ key ] = {"btc_options":btc_options, "btc_market":btc_market,  "param_matrix":param_matrix, "m":m, "iv_ssvi":iv_ssvi}
#         except:
#             Cache[ key ] = None    

#     nasdaq_key =  f"nasdaq:{ticker}:{ref_date1}"
#     if nasdaq_key not in Cache:
#         try:
#             #ndata= get_nasdaq_option_data( ref_date1, ticker )    
#             ndata= get_iv_data( ref_date1, ticker )

#             ndata['log_moneyness'] = np.log(ndata['strike']/ndata['spot'])
#             Cache[ nasdaq_key ] = ndata
#         except:
#             Cache[ nasdaq_key ] = None    

#     nasdaq_data = Cache.get(nasdaq_key, None)

#     if (key in Cache) and ( Cache[ key ] is not None):
#         btc_options = Cache[ key ]["btc_options"]
#         btc_market = Cache[ key ]["btc_market"]
#         param_matrix = Cache[ key ]["param_matrix"]
#         m = Cache[ key ]["m"]
#         iv_ssvi = Cache[ key ]["iv_ssvi"]

#         spot= btc_options['underlying_price'].iloc[0]
#         m_strike = [ math.exp(x)*spot for x in m]

#         print("---------param matrix ----------")
#         print(param_matrix)

#         if xaxis_type == 'strike':
#             xfield = 'strike'
#             plot_x = m_strike
#         elif xaxis_type == 'log(K/S)':
#             xfield = 'log_moneyness'
#             plot_x = m
            
#         x_min = 100
#         x_max = -100
#         y_min = 100
#         y_max = -100
#         k = 0
#         plots= []
#         price_plots= []
#         params_str=""
#         num_colors = len(pio.templates[pio.templates.default]['layout']['colorway'])

#         ##############
#         if adjust_fit and (adjust_term != "") and (explore_num_params != num_params):
#             key_adj= f"{ticker}:{ref_date1}:{explore_num_params}"
#             if key_adj not in Cache:
#                 try:
#                     btc_options_A, btc_market_A,  param_matrix_A, m_A, iv_ssvi_A = do_fit_and_plots( ticker, model = model, ref_date = ref_date1, num_params=explore_num_params, num_strike_points = num_strike_points, pricing_model=pricing_model, use_borrow_from_db =use_borrow_from_db )
#                     Cache[ key_adj ] = {"btc_options":btc_options_A, "btc_market":btc_market_A,  "param_matrix":param_matrix_A, "m":m_A, "iv_ssvi":iv_ssvi_A}
#                 except:
#                     Cache[ key_adj ] = None
#             else:
#                 btc_options_A = Cache[ key_adj ]["btc_options"]
#                 btc_market_A = Cache[ key_adj ]["btc_market"]
#                 param_matrix_A = Cache[ key_adj ]["param_matrix"]
#                 m_A = Cache[ key_adj ]["m"]
#                 iv_ssvi_A = Cache[ key_adj ]["iv_ssvi"]        
#         else:
#             btc_options_A=btc_options
#             btc_market_A=btc_market  
#             param_matrix_A=param_matrix
#             m_A=m 
#             iv_ssvi_A=iv_ssvi                 
#         ##############

#         for i,T in enumerate(btc_market['time_to_expiry_yrs'].unique()):
            
#             marker_color = pio.templates[pio.templates.default]['layout']['colorway'][i%num_colors]
#             mkt = btc_market[btc_market['time_to_expiry_yrs'] == T ]
#             mkt['opt_type'] = mkt['option_type'].apply(lambda x: x[0].upper())

#             mkt_by_opt_type ={}
#             for f in ['C','P']:
#                 mkt_by_opt_type[f] = mkt[mkt['opt_type']==f]

#             term = mkt['expiration_date'].iloc[0]
            
#             term_str = term.strftime("%Y-%m-%d")
#             print(f"term_str {term_str}, {type(term)} selected_terms {selected_terms}")
#             if (term_str not in selected_terms) and not (adjust_fit and (term_str == adjust_term)):
#                 continue

#             real_m = btc_market.loc[btc_market['time_to_expiry_yrs']==T, xfield]
#             #real_iv = btc_market.loc[btc_market['time_to_expiry_yrs']==T, 'mid_iv']
#             real_iv = mkt['mid_iv']
#             real_iv_spread = np.array((mkt['IV_ask'] - mkt['IV_bid']).abs()/2)
#             real_iv_var_spread = np.array((mkt['IV_ask']*mkt['IV_ask'] - mkt['IV_bid']*mkt['IV_bid']).abs()/2)
            
#             '''
#             real_m_by_opt_type={}
#             real_iv_by_opt_type={}
#             real_iv_spread_by_opt_type={}
#             real_iv_var_spread_by_opt_type={}
            
#             for f in ['C','P']:
#                 real_m_by_opt_type[f] = real_m[real_m['opt_type']==f]
#                 real_iv_by_opt_type[f] = real_iv[real_iv['opt_type']==f]
#                 real_iv_spread_by_opt_type[f] = real_iv_spread[real_iv_spread['opt_type']==f]
#                 real_iv_var_spread_by_opt_type[f] = real_iv_var_spread[real_iv_var_spread['opt_type']==f]
#             '''
#             y_real_val_by_opt_type ={}
#             y_real_val_spread_by_opt_type={}
#             y_val_by_opt_type ={}
#             if yaxis_type == 'vol':
#                 y_real_val = real_iv
#                 y_real_val_spread = real_iv_spread   
#                 y_val = iv_ssvi[T]

#                 '''
#                 for f in ['C','P']:
#                     y_real_val_by_opt_type[f] = real_iv_by_opt_type[f]
#                     y_real_val_spread_by_opt_type[f] = real_iv_spread_by_opt_type[f]
#                     #y_val_by_opt_type[f] = 
#                 '''
#             elif yaxis_type == 'var':
#                 y_real_val = [x*x for x in real_iv]
#                 y_real_val_spread = real_iv_var_spread
#                 y_val = [x*x for x in iv_ssvi[T]]

#             xpad = (max(real_m) - min(real_m))/20
#             ypad = (max(y_real_val) - min(y_real_val))/20
            
#             x_min= min(x_min, min(real_m)) -xpad
#             x_max= max(x_max, max(real_m)) +xpad
#             y_min= min(y_min, min(y_real_val))-ypad
#             y_max= max(y_max, max(y_real_val))+ypad
            
            
#             if model_data is None:
#                 model_term_data = None
#             else:
#                 model_term_data = model_data[model_data['TERM']== term]
#                 if len(model_term_data) == 0:
#                     model_term_data = model_data[model_data['TERM']== null_date]
#                     if len(model_term_data) == 0:
#                         model_term_data = None
#                     else:
#                         model_term_data = model_term_data.iloc[0]    
#                 else:
#                     model_term_data = model_term_data.iloc[0]

#             #if ticker in fitting_models_by_ticker:
#             if ( model_term_data is not None ) and ( model_term_data['MODEL'] == 'spline') :

#                 weights =[ 1/max(x, 0.01) for x in y_real_val_spread]
#                 #tck = splrep(real_m,y_real_val, s=fitting_models_by_ticker[ticker], k=3, w=weights)
#                 tck = splrep(real_m,y_real_val, s=model_term_data['MODEL_PARAM'], k=3, w=weights)
                
#                 real_min = list(real_m)[0] 
#                 real_max = list(real_m)[len(real_m)-1] 
#                 plot_x1 = list( filter( lambda x: ( x <= real_max) and (x >= real_min ), plot_x ) )

#                 fitted_spline = splev(plot_x1, tck)

#                 plots.append( go.Scatter(
#                     name=f'{term} : spline',
#                     x=plot_x1,
#                     y=fitted_spline,
#                     #error_y=error_y,
#                     #mode='markers',
#                     #marker=dict(size=8, symbol="circle", color = marker_color),
#                     showlegend=True
#                 ))

#             if ( model_term_data is None ) or ( model_term_data['MODEL'] == 'JW') :
            
#                 plots.append( go.Scatter(
#                     name=f'{term}',
#                     x=plot_x    ,
#                     y=y_val,
#                     #mode='markers',
#                     #marker=dict(color='red', size=2),
#                     showlegend=True,
#                     line=dict(color = marker_color)
                    
#                 ))
#             if show_error_bars:
#                 error_y= dict(
#                         type='data', # value of error bar given in data coordinates
#                         thickness=0.5,
#                         width=3,
#                         array=y_real_val_spread, visible=True)
#             else:
#                 error_y =None

#             plots.append( go.Scatter(
#                 name=f'{term}',
#                 x=real_m,
#                 y=y_real_val,
#                 error_y=error_y,
#                 mode='markers',
#                 marker=dict(size=8, symbol="circle", color = marker_color),
#                 showlegend=False
#             ))
            

#             nasdaq_term_data=[]
#             if nasdaq_data is not None:
#                 nasdaq_term_data = nasdaq_data[nasdaq_data['term']==term_str]
#                 if len(nasdaq_term_data)>0:

#                     y_min= min(y_min, min(nasdaq_term_data['imp_vol']))-ypad
#                     y_max= max(y_max, max(nasdaq_term_data['imp_vol']))+ypad

#                     plots.append( go.Scatter(
#                         name=f'{term}:nasdaq',
#                         x=nasdaq_term_data[xfield],
#                         y=nasdaq_term_data['imp_vol'],
#                         mode='markers',
#                         marker=dict(size=10, 
#                                     symbol="circle", 
#                                     color = marker_color,
#                                     line=dict(color='MediumPurple',width=4),
#                                     #color='LightSkyBlue',          
#                                 ),
                       
            
#                         showlegend=True
#                     ))
            
            

#             for otype in ['C', 'P']:
#                 mkt1 = mkt[mkt['opt_type']==otype]
#                 spread1 = (mkt1['ASK']-mkt1['BID']).abs()
                
#                 if otype == 'C':
#                     marker_symbol = 'circle-open'
#                 else:
#                     marker_symbol = 'circle'

#                 price_error_y= dict(
#                         type='data', # value of error bar given in data coordinates
#                         thickness=0.5,
#                         width=3,
#                         array=list(spread1/2), visible=True)
                
#                 price_plots.append( go.Scatter(
#                         name=f'{term}',
#                         x=mkt1[xfield],
#                         y=(mkt1['BID']+mkt1['ASK'])/2,
#                         error_y=price_error_y,
#                         mode='markers',
#                         marker=dict( symbol = marker_symbol ),
#                         showlegend= (otype == 'P'),
#                         line=dict(color = marker_color )
                        
#                     ))    
#                 if len(nasdaq_term_data)>0:
#                     nas1 = nasdaq_term_data[nasdaq_term_data['opt_type']==otype]
#                     price_plots.append( go.Scatter(
#                         name=f'{term}:{otype}:nasdaq',
#                         x=nas1[xfield],
#                         y=nas1['price'],
#                         mode='markers',
#                         marker=dict( symbol = marker_symbol, color = marker_color,
#                                     line=dict(color='MediumPurple',width=2), ),
#                         #marker=dict(color='red', size=2),
#                         showlegend=True,
#                         line=dict(color = marker_color )
                        
#                     )) 
#             if adjust_fit and (term_str == adjust_term):

#                 params= list(param_matrix_A[T])
#                 new_params = params.copy()
                
#                 new_params[0] *= mult_param_a1
#                 new_params[1] *= mult_param_b1
#                 new_params[2] *= mult_param_a2
#                 new_params[3] *= mult_param_b2
                
#                 #new_params = [params[0]*mult_param_a1,params[1]*mult_param_b1,params[2]*mult_param_a2,params[3]*mult_param_b2]
                
#                 if model == 'jw':
#                     adj_var = np.array([max(0,raw_jw(x, *new_params )) for x in m])
#                 elif model == 'cc':
#                     adj_var = np.array([max(0,raw_cc(x, new_params )) for x in m])

#                 adj_vol = adj_var**0.5
#                 if yaxis_type == 'vol':
#                     y_val_adj = adj_vol
#                 elif yaxis_type == 'var':
#                     y_val_adj = adj_var

#                 res = np.array(residual_model(params,T, btc_market_A, model ))
#                 objective = np.sum(res**2)
#                 res_new = np.array(residual_model(new_params,T, btc_market_A, model))
#                 objective_new = np.sum(res_new**2)
#                 objective_str =f" new: {objective_new:.4f},  old: {objective:.4f}"
#                 num_cols= 3
#                 num_rows = int(math.ceil(len(params)/num_cols))
#                 fig_tmp = make_subplots( rows = num_rows, cols=num_cols, start_cell="top-left")
#                 for j in range(len(params)):
#                     param_color = pio.templates[pio.templates.default]['layout']['colorway'][j%num_colors]
#                     vals=[]
#                     xvals=[]
#                     for mult in range(50,200,1):
#                         mult= mult/100 
#                         params_tmp = params.copy()
#                         params_tmp[j] *= mult
#                         xvals.append(params_tmp[j])
#                         res_tmp = np.array(residual_model(params_tmp,T, btc_market_A, model))
#                         vals.append( np.sum(res_tmp**2) )
                    
#                     vals1=[]
#                     xvals1=[]
#                     for mult in range(50,200,1):
#                         mult= mult/100
#                         params_tmp = new_params.copy()
#                         params_tmp[j] *= mult
#                         xvals1.append(params_tmp[j])
#                         res_tmp = np.array(residual_model(params_tmp,T, btc_market_A, model))
#                         vals1.append( np.sum(res_tmp**2) )

#                     if j in [0,1]:
#                         row = 1
#                     elif j in [2,3]:
#                         row = 2
#                     else:
#                         row=2   
#                     row = int(math.floor((j)/num_cols))+1
#                     col = j%num_cols+1
                    
#                     row = min(row, num_rows)
#                     col = min(col, num_cols)
#                     print(f'row, col ( {row}, {col} )')

#                     fig_tmp.add_trace(
#                         go.Scatter(
#                         name=f'param {j}',
#                         x=xvals,
#                         y=vals,
#                         showlegend=True,
#                         line=dict(color= param_color )
#                     ),row=row, col=col)
#                     fig_tmp.add_trace(
#                         go.Scatter(
#                         name=f'param {j}',
#                         x=xvals1,
#                         y=vals1,
#                         showlegend=False,
#                         line=dict( dash='dash', color= param_color )
#                     ),row=row, col=col)

#                     fig_tmp.add_trace(
#                         go.Scatter(
#                         name=f'new',
#                         x=[new_params[j]],
#                         y=[objective_new],
#                         showlegend=(j==len(params)-1),
#                         mode='markers',
#                         marker=dict(size=8, symbol="circle", color = 'red'),
#                     ),row=row, col=col)

#                     fig_tmp.add_trace(
#                         go.Scatter(
#                         name=f'old',
#                         x=[params[j]],
#                         y=[objective],
#                         showlegend=(j==len(params)-1),
#                         mode='markers',
#                         marker=dict(size=8, symbol="circle", color = 'blue'),
#                     ),row=row, col=col)
                    
                    

                    
#                 fig_tmp.update_layout(
#                         # xaxis_title="param value",
#                         # yaxis_title="fit residual",
#                         title=f'fit residual',
#                         height=305,
#                         width=500,
#                     )
                    
#                 fig_tmp.update_yaxes(row=1, col=1, patch= {'tickformat' : '.2f'})
#                 res_figs.append( dcc.Graph( figure = fig_tmp ) ) 
                   
#                 plots.append( go.Scatter(
#                     name=f'{term}',
#                     x=plot_x,
#                     y=y_val_adj,
#                     #mode='markers',
#                     #marker=dict(color='red', size=2),
#                     showlegend=True,
#                     line=dict(color = marker_color, dash='dash' )
                    
#                 ))    
                
#                 params_str = f" { ' '.join([f"{x:.4f}" for x in new_params])}"

#                 ##############  do spline 
#                 weights =[ 1/max(x, 0.01) for x in y_real_val_spread]
                
#                 if adjust_spline_tension is not None:
#                     tck = splrep(real_m,y_real_val, s=adjust_spline_tension, k=3, w=weights)
#                     fitted_spline = splev(plot_x, tck)
                    
#                     plots.append( go.Scatter(
#                     name=f"{term} : spline s = {adjust_spline_tension : .4f}",
#                     x=plot_x,
#                     y=fitted_spline,
#                     showlegend=True,
#                     line=dict(color = marker_color, dash='dot' )
#                 ))


#             k+=1
#         fig = go.Figure(plots)
#         fig.update_layout(
#             xaxis_title=xaxis_type,
#             yaxis_title=yaxis_type,
            
#             title=f'{ticker} on {ref_date1}',
#             #hovermode="x",
#             #yaxis1 = {'tickformat' : '.2f'},
#             height=500
#         )
#         fig.update_xaxes(range=[x_min, x_max] )
#         fig.update_yaxes(range=[y_min, y_max])

#         print("m:",(m))
#         print(f"range [{x_min},{x_max}]")
#         fig['layout']['xaxis'] = {'range': (x_min, x_max)}

#         ##################
#         fig_price = go.Figure(price_plots)
#         fig_price.update_layout(
#             xaxis_title=xfield,
#             yaxis_title='option price',
            
#             title=f'Price for {ticker} on {ref_date1}',
#             #hovermode="x",
#             #yaxis1 = {'tickformat' : '.2f'},
#             height=500
#         )
#         ###################


#         #fig.show()
#         interpolate = False
#         X,Y,Z= get_surf_mesh(btc_market, m, iv_ssvi, interpolate, no_points=25)
#         #print(X)
#         #print(Y)
#         #print(Z)
#         fig2 = go.Figure()
#         fig2.add_trace( 
#                     go.Mesh3d(x=btc_market['time_to_expiry_yrs'],
#                     y=btc_market['log_moneyness'],
#                     z=btc_market['mid_iv'],
#                     opacity=0.7,
#                     color='rgba(244,22,100,0.6)'
#                     )
#         )

#         fig2.update_layout(
#             scene = dict( 
#                       xaxis=dict( title=dict( text='time to expiry years' )),
#                       yaxis=dict( title=dict( text="log(K/S)" )),
#                       zaxis=dict( title=dict( text='vol' )),
#                       ),
            
#             title=f'{ticker} on {ref_date1}',
#             #hovermode="x",
#             height=700
#         )

#         terms= list(np.unique(btc_market['expiration_date']))
#         terms.sort()
#         terms_str = [x.strftime("%Y-%m-%d") for x in terms]

#         hid_adj_panel = (adjust_term=="" or (adjust_term not in terms_str))

#         return fig, fig_price, fig2, (not adjust_fit ), params_str, adjust_term, objective_str, res_figs, hid_adj_panel , spline_figs, hid_adj_panel, fitting_model_info
#     status = f'no mkt data for {ticker} on {ref_date1}'
#     return go.Figure(), go.Figure(), go.Figure(), False, "", "","",[], True, [], False, fitting_model_info


# if __name__ == '__main__':
#     app.run(debug=True)
