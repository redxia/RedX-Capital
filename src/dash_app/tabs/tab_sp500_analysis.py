import plotly.graph_objs as go
from dash.exceptions import PreventUpdate
import numpy as np
from dash import Dash, html, dcc, callback, Output, Input, ctx 
from dash import html, dcc, callback
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots
import pandas as pd
import importlib
from download_data import download
from datetime import timedelta
import plotly.express as px  # For color palettes
import dash_table
import warnings
warnings.filterwarnings('ignore')

color_palette = px.colors.qualitative.Plotly 

df, pivot_df, pivot_df_cumulative, most_correlated_years=download.spy_download()
vix, vix_3mo = download.vix_downloads()
df=df.merge(vix, on='Date', how='left')
df=df.merge(vix_3mo, on='Date', how='left')
df['3M_0M_VIX'] = df['^VIX3M'] / df['^VIX'] - 1
vix_levels=vix['^VIX'].quantile([0,.2,.4,.6,.8,.9,1]).reset_index().rename(columns={'index':'quintile'}).round(2)
#TODO show the panel for the other stuff.
# need to do bar graph of the returns.
# include the months.
#TODO callback to see other years

tab_sp_analysis = dcc.Tab(
    label="S&P 500",
    children=[
        # html.Div(style={"clear": "both"}),
        html.H1(children="S&P 500 Analysis", style={"textAlign": "center"}),
        html.Div(style={"clear": "both"}),
        html.Div(children=[
            html.Div([
            html.Button(
                "Refresh",
                id='refresh-data',
                n_clicks=0,
                style={
                    "margin-left": "15px",
                    "margin-right": "0px",
                    "margin-top": "15px",
                    "float": "left",
                    "font-weight": "bold",
                }
            ),                
            html.Div(id='latest-date'),
            html.Div(id='latest-day'),
            html.Div(id='latest-close'),
            html.Div(id='latest-returns'),
            html.Div(id='latest-vix-bucket'),
            html.Div(id='latest-vix'),
            html.Div(id='latest-3month-vix'),
            html.Div(id='latest-3month-0month-vix'),
            html.Div(id='latest-drawdown')],
                style={
                'display': 'flex',
                'justifyContent': 'center',
                'alignItems': 'center',
                'flexWrap': 'wrap',
                'gap': '20px',
                'font-size':'20px'
            }),
            html.Div(children=[
                html.Br(style={'width': '100%'}),
                html.Div(id='latest-5d-ret'),
                html.Div(id='latest-10d-ret'),
                html.Div(id='latest-21d-ret'),
                html.Div(id='latest-1yr-ret'),
                html.Div(id='latest-200d-pct-ret')
                ],
                    style={
                    'display': 'flex',
                    'justifyContent': 'center',
                    'alignItems': 'center',
                    'flexWrap': 'wrap',
                    'gap': '20px',
                    'font-size':'20px'
                    }
                ),
            html.Div(children=[
                html.Br(style={'width': '100%'}),
                html.Div(id='forecast-negative-ret'),
                html.Div(id='forecast-returns'),
                html.Div(id='forecast-positive-ret'),
                html.Div('|'),
                html.Div(id='forecast-negative-level'),
                html.Div(id='forecast-level'),
                html.Div(id='forecast-positive-level')
                ],
                style={
                    'display': 'flex',
                    'justifyContent': 'center',
                    'alignItems': 'center',
                    'flexWrap': 'wrap',
                    'gap': '20px',
                    'font-size':'20px'
                    })
                ]),
        html.Div(style={"clear": "both"}),
        html.Div(children=[
                dcc.Graph(id="candlestick-chart", 
                    style={"width": "98vw", "height": "80vh"}), 
                html.Div('Moving Average cross over. If it crosses red then there is momentum to the down side. Sell/Hedge. Green it a buy. 200D MA hits 1-2 a year'),
                dcc.Graph(id="ma-crossover", 
                  style={"width": "93vw", "height": "35vh", 'margin-top':'2px'}),
                dcc.Graph(id="dist-200MA", 
                  style={"width": "98vw", "height": "75vh", 'margin-top':'2px'}),
                dcc.Graph(id="daily-returns", 
                  style={"width": "98vw", "height": "75vh", 'margin-top':'2px'}),
                html.Div('If 21STD passes the VIX, then in general it is a bottoming signal. Closing gap is momentum.'),
                html.Pre([vix_levels.to_string(),(100*df['DIST_200MA'].describe().round(4)).to_string()], style={'fontSize': '20px', 'margin': '10px', 'whiteSpace': 'pre-wrap', 'display': 'flex'}),
                # html.Pre(, style={'fontSize': '20px', 'margin': '10px', 'whiteSpace': 'pre-wrap','display': 'flex'}),
                dcc.Graph(id="vix", 
                  style={"width": "98vw", "height": "80vh", 'margin-top':'2px'}),
                html.Div('3month vs. spot vix. Under 0 is buy. over .2 is sell or hedge. Realized vs. VIX converging back to 0 is a buy and huge spikes are sells/hedge'),
                dcc.Graph(id="seasonal-volaility", 
                  style={"width": "98vw", "height": "80vh", 'margin-top':'2px'}),
                dcc.Graph(id="short-mid-volaility", 
                  style={"width": "98vw", "height": "80vh", 'margin-top':'2px'})
            ]),
        html.Div(style={"clear": "both"}),
        html.Div(children=[
            dcc.Graph(id="correlated-year", 
                  style={"width": "98vw", "height": "75vh"}),             
            dcc.Graph(id="seasonal-year", 
                  style={"width": "98vw", "height": "55vh"})
        ]),
        html.Div(style={"clear": "both"}),
        html.Label("Year: ",style={'margin-right':'10px', "float": "left", 'margin-top':'8px','font-size':'18px','margin-left':'8px'}),
        dcc.Dropdown(
            options=pivot_df_cumulative.columns.to_list(),
            value=pivot_df_cumulative.columns[-1],
            multi=True,
            id="year",
            style={"margin-left": "5px", "width": "40vw", "float": "left"}, # 
        ),
        html.Div(style={"clear": "both"}),
        dcc.Graph(id="year-perf", 
                  style={"width": "98vw", "height": "75vh"}), 
        html.Div(style={"clear": "both"}),
        dcc.Graph(id="drawdown-plot", 
                  style={"width": "98vw", "height": "90vh"}), 
        html.Div(style={"clear": "both"}),
                dcc.Graph(id="year-drawdown-plot", 
                  style={"width": "98vw", "height": "75vh"}), 
        html.Div(style={"clear": "both"}),
        html.Div(children=[
                dcc.Graph(id="monthly-seasonality", 
                  style={"width": "98vw", "height": "75vh", 'margin-top':'2px'}),
                dash_table.DataTable(
                    id='statistics',
                    style_table={'overflowX': 'auto'},
                    style_cell={
                        'textAlign': 'center',
                        'backgroundColor': '#1f2c56',
                        'color': 'white',
                        'fontFamily': 'Arial',
                        'fontSize': '14px',
                        'border': '1px solid #313a46',
                    },
                    style_header={
                        'backgroundColor': '#4CAF50',
                        'fontWeight': 'bold',
                        'color': 'white',
                        'border': '1px solid #313a46',
                    }),
                dcc.Graph(id="monthly-returns", 
                  style={"width": "98vw", "height": "75vh", 'margin-top':'2px'}),
                dcc.Graph(id="yearly-returns", 
                  style={"width": "98vw", "height": "75vh", 'margin-top':'2px'})
        ])
    ]
)


@callback(
    [
         
        Output('latest-date', "children"),
        Output('latest-day', "children"),
        Output('latest-close', "children"),
        Output('latest-returns', "children"),
        Output('latest-vix-bucket', "children"),
        Output('latest-vix', "children"),
        Output('latest-3month-vix', "children"),
        Output('latest-3month-0month-vix', "children"),
        Output('latest-drawdown', "children"),
        Output('latest-5d-ret', "children"),
        Output('latest-10d-ret', "children"),
        Output('latest-21d-ret', "children"),
        Output('latest-1yr-ret', "children"),
        Output('latest-200d-pct-ret', "children"),

        Output('forecast-negative-ret', "children"),
        Output('forecast-returns', "children"),
        Output('forecast-positive-ret', "children"),
        
        Output('forecast-negative-level', "children"),
        Output('forecast-level', "children"),
        Output('forecast-positive-level', "children"),
        

        Output("candlestick-chart", "figure"),
        Output("ma-crossover", "figure"),
        Output("dist-200MA", "figure"),
        Output("daily-returns", "figure"),
        Output("vix", "figure"),
        Output("seasonal-volaility", "figure"),
        Output("short-mid-volaility", "figure"),
        Output("correlated-year", "figure"),
        Output("seasonal-year", "figure"),
        Output("year-perf", "figure"),
        Output("drawdown-plot", "figure"),
        Output("year-drawdown-plot", "figure"),
        Output('monthly-seasonality', "figure"),
        Output("statistics", "data"),
        Output("monthly-returns", "figure"),
        Output("yearly-returns", "figure")
          
    ],
    [
        Input("refresh-data", "n_clicks"),
        Input("year", "value")
    ],
)
def update_graph(
    n_clicks,
    year
    # relayoutDataVolatility,
    # relayoutDataParameters,
) -> list:
    # if n_clicks >= 0:
    if n_clicks is None:
        return go.Figure()
    print(f"Refresh {n_clicks}") 
    importlib.reload(download)
    df, pivot_df, pivot_df_cumulative, most_correlated_years=download.spy_download()
    vix, vix_3mo = download.vix_downloads()
    df=df.merge(vix, on='Date', how='left')
    df=df.merge(vix_3mo, on='Date', how='left')
    print(df.tail())
    
    monthly_ret=download.monthly_returns(df.copy())
    yearly_ret=download.yearly_returns(df.copy())
    df['3M_0M_VIX'] = df['^VIX3M'] / df['^VIX'] - 1

    
    lastest_bucket=vix['VIX'].iloc[-1]

    try:
        analysis_0=download.std_dev_offset(datas=df.copy(), vix_bucket=lastest_bucket-1)
        analysis_0=analysis_0.T
        analysis_0.columns=['SPY_'+str(lastest_bucket-1), 'VIX_'+str(lastest_bucket-1)]
        analysis_0=analysis_0.iloc[1:]
    except:
        pass
    analysis_1=download.std_dev_offset(datas=df.copy(), vix_bucket=lastest_bucket)
    analysis_1=analysis_1.T
    analysis_1.columns=['SPY_'+str(lastest_bucket), 'VIX_'+str(lastest_bucket)]
    analysis_1=analysis_1.iloc[1:]
    
    try:
        analysis_2=download.std_dev_offset(datas=df.copy(), vix_bucket=lastest_bucket+1)
        analysis_2=analysis_2.T
        analysis_2.columns=['SPY_'+str(lastest_bucket+1), 'VIX_'+str(lastest_bucket+1)]
        analysis_2=analysis_2.iloc[1:]
    except:
        pass
    
    try:
        total_frame=pd.concat([analysis_0, analysis_1], axis=1)
    except:
        pass
    
    try:
        total_frame=pd.concat([total_frame, analysis_2], axis=1)
    except:
        pass
    total_frame.reset_index(names='Symbol', inplace=True)

    analysis=download.std_dev_offset(datas=df.copy(), vix_bucket=lastest_bucket, aggregator=21)
    analysis=analysis.T
    analysis.columns=['21_SPY_'+str(lastest_bucket), '21_VIX_'+str(lastest_bucket)]
    analysis=analysis.iloc[1:]


    filtered_df = df.iloc[-(252 * 3) :]  # last 3 years
    
    most_correlated_df=pivot_df_cumulative[most_correlated_years.index].round(4) * 100
    latest_year=most_correlated_years.index[-1]
    
    # ytd_filter=pivot_df_cumulative[year]
    # print(ytd_filter)
    # year=list(year)
    # years=pivot_df_cumulative.columns
        
    price_fig = go.Figure(data=[go.Candlestick(
        x=filtered_df['Date'],
        open=filtered_df["Open"],
        high=filtered_df["High"],
        low=filtered_df["Low"],
        close=filtered_df["Close"],
        name="SPY"
    )])
    price_fig.add_trace(go.Scatter(
        x=filtered_df['Date'],
        y=filtered_df["200D_EWMA"],
        mode="lines",
        name="200-Day EWMA",
        line=dict(color="darkgreen", width=2)
    ))
    price_fig.add_trace(go.Scatter(
        x=filtered_df['Date'],
        y=filtered_df["10D_EWMA"],
        mode="lines",
        name="10-Day EWMA",
        line=dict(color="blue", width=2)
    ))
    price_fig.add_trace(go.Scatter(
        x=filtered_df['Date'],
        y=filtered_df["30D_EWMA"],
        mode="lines",
        name="30-Day EWMA",
        line=dict(color="brown", width=2)
    ))
    price_fig.update_layout(
        title="SPY",
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        autosize=True,
        xaxis=dict(
            title="Date",
            range=[filtered_df['Date'].min()-timedelta(days=10), filtered_df['Date'].max()+timedelta(days=10)]  # Ensure full date range is visible
        )
    )
    
    colors = ["green" if val >= 0 else "red" for val in filtered_df['MA_CROSSOVER'].round(2)]
    ma_cross_fig = go.Figure()
    ma_cross_fig.add_trace(go.Bar(
        x=filtered_df['Date'], 
        y=filtered_df['MA_CROSSOVER'].round(2),
        marker=dict(color=colors)
        # name="Moving Average Cross Over"
    ))
    ma_cross_fig.update_layout(
        title="Moving Average Cross Over 10D-30D",
        xaxis_title="Date",
        yaxis_title="Range",
        autosize=True,
        showlegend=False,
        xaxis=dict(
            title="Date",
            range=[filtered_df['Date'].min()-timedelta(days=10), filtered_df['Date'].max()+timedelta(days=10)]  # Ensure full date range is visible
        )#
    )

    dist_200MA_fig = go.Figure()
    dist_200MA_fig.add_trace(go.Scatter(
        x=filtered_df['Date'], 
        y=filtered_df['DIST_200MA'].round(4)*100,
        mode='lines',
        line={'color':'blue','width':2},
        name="200MA Return"
    ))
    dist_200MA_fig.update_layout(
        title="Return from 200 EWMA",
        xaxis_title="Date",
        yaxis_title="Returns",
        autosize=True,
        showlegend=True,
        xaxis=dict(
            title="Date",
            range=[filtered_df['Date'].min()-timedelta(days=10), filtered_df['Date'].max()+timedelta(days=10)]  # Ensure full date range is visible
        )
    )

    vix_fig = go.Figure()
    vix_fig.add_trace(go.Scatter(
        x=filtered_df['Date'], 
        y=filtered_df['21D_STD'].round(4)*100,
        mode='lines',
        line={'color':'black','width':2},
        name="21D STD"
    ))
    vix_fig.add_trace(go.Scatter(
        x=filtered_df['Date'], 
        y=filtered_df['^VIX'].round(2),
        mode='lines',
        line={'color':'blue','width':2},
        name="VIX"
    ))
    vix_fig.add_trace(go.Scatter(
        x=filtered_df['Date'], 
        y=filtered_df['^VIX3M'].round(2),
        mode='lines',
        line={'color':'green','width':2},
        name="VIX 3 Month"
    ))
    vix_fig.update_layout(
        title="VIX Levels",
        xaxis_title="Date",
        yaxis_title="Volatility",
        autosize=True,
        showlegend=True,
        xaxis=dict(
            title="Date",
            range=[filtered_df['Date'].min()-timedelta(days=10), filtered_df['Date'].max()+timedelta(days=10)]  # Ensure full date range is visible
        )
    )


    short_mid_vix_fig = go.Figure()
    short_mid_vix_fig.add_trace(go.Scatter(
        x=filtered_df['Date'], 
        y=filtered_df['3M_0M_VIX'].round(2),
        mode='lines',
        line={'color':'blue','width':2},
        name="3M/0M VIX"
    ))
    short_mid_vix_fig.add_trace(go.Scatter(
        x=filtered_df['Date'], 
        y=(filtered_df['^VIX']/(filtered_df['21D_STD']*100)-1).round(2),
        mode='lines',
        line={'color':'black','width':2},
        name="VIX vs. Realized"
    ))
    short_mid_vix_fig.update_layout(
        title="Mid Short Term VIX",
        xaxis_title="Date",
        yaxis_title="Volatility",
        autosize=True,
        showlegend=True,
        xaxis=dict(
            title="Date",
            range=[filtered_df['Date'].min()-timedelta(days=10), filtered_df['Date'].max()+timedelta(days=10)]  # Ensure full date range is visible
        )
    )

    seasonal_volatility=df.groupby('Day', as_index=False)[['21D_STD','^VIX']].mean().merge(df.groupby('Day', as_index=False)['Returns'].std(), on='Day', how='left').iloc[:-2]
    
    # df.groupby('Day')['21D_STD'].mean()
    # df.groupby('Day')['^VIX'].mean()
    # df.groupby('Day')['Returns'].std()

    vix_seasonality_fig = go.Figure()
    vix_seasonality_fig.add_trace(go.Scatter(
        x=seasonal_volatility['Day'], 
        y=seasonal_volatility['21D_STD'].round(4)*100,
        mode='lines',
        line={'color':'black','width':2},
        name="21D STD"
    ))
    vix_seasonality_fig.add_trace(go.Scatter(
        x=seasonal_volatility['Day'], 
        y=seasonal_volatility['^VIX'].round(2),
        mode='lines',
        line={'color':'blue','width':2},
        name="VIX"
    ))
    vix_seasonality_fig.add_trace(go.Scatter(
        x=seasonal_volatility['Day'], 
        y=seasonal_volatility['Returns'].round(4)*100,
        mode='lines',
        line={'color':'green','width':2},
        name="STD Returns",
        yaxis='y2'
    ))    
    vix_seasonality_fig.update_layout(
        title="Seasonal Volatility",
        xaxis_title="Day",
        yaxis_title="Volatility",
        autosize=True,
        showlegend=True,
        yaxis2=dict(overlaying='y', side='right')
        # xaxis=dict(
        #     title="Date",
        #     range=[filtered_df['Date'].min()-timedelta(days=10), filtered_df['Date'].max()+timedelta(days=10)]  # Ensure full date range is visible
        # )#
    ) #TODO look at vix seasonality.


    correlation_fig = go.Figure()
    for i, col in enumerate(most_correlated_df.columns):
        correlation_fig.add_trace(go.Scatter(
            x=most_correlated_df[col].index, 
            y=most_correlated_df[col], 
            mode="lines+markers", 
            name=col,
            line=dict(color=color_palette[i % len(color_palette)])  
        ))    
    correlation_fig.update_layout(
        title="Years",
        xaxis_title="Days",
        yaxis_title="YTD Returns",
        xaxis_rangeslider_visible=False,
        autosize=True
    )

    ytd_fig = go.Figure()
    if type(year) == int:
        ytd_fig.add_trace(go.Scatter(
            x=pivot_df_cumulative[year].index, 
            y=(pivot_df_cumulative[year].round(4))*100, 
            mode="lines+markers", 
            name=year))
    else:
        for idx, yr in enumerate(pivot_df_cumulative[year].columns):
            ytd_fig.add_trace(go.Scatter(
                x=pivot_df_cumulative[yr].index, 
                y=(pivot_df_cumulative[yr].round(4))*100,
                mode="lines+markers", 
                name=str(yr),
                line=dict(color=color_palette[idx % len(color_palette)])  
            ))
    ytd_fig.update_layout(
        title="Year ",
        xaxis_title="Days",
        yaxis_title="YTD Returns",
        xaxis_rangeslider_visible=False,
        autosize=True
    ) 
    
    seasonal_fig = go.Figure()
    seasonal_fig.add_trace(go.Scatter(
        x=pivot_df_cumulative.index, 
        y=pivot_df_cumulative.mean(axis=1).round(4) * 100, 
        mode="lines+markers", 
        name='YTD Seasonality'
    ))
    seasonal_fig.add_trace(go.Scatter(
        x=pivot_df.index, 
        y=2*(pivot_df.std(axis=1).round(4) * 100) + pivot_df_cumulative.mean(axis=1).round(4) * 100, 
        mode="lines+markers", 
        name='+2 STD'
    ))
    seasonal_fig.add_trace(go.Scatter(
        x=pivot_df.index, 
        y=-2*(pivot_df.std(axis=1).round(4) * 100) + pivot_df_cumulative.mean(axis=1).round(4) * 100, 
        mode="lines+markers", 
        name='-2 STD'
    ))
    seasonal_fig.update_layout(
        title="Average Years",
        xaxis_title="Days",
        yaxis_title="YTD Returns",
        xaxis_rangeslider_visible=False,
        autosize=True
    ) 
    # pivot_df_cumulative.mean(axis=1).plot()

    drawdown_fig = go.Figure()
    drawdown_fig.add_trace(go.Scatter(
        x=filtered_df['Date'], 
        y=filtered_df['Drawdown'].round(4)*100,
        mode='lines',
        fill='tozeroy',
        line=dict(color='blue'),
        name="Under Water Plot"
    ))
    drawdown_fig.update_layout(
        title="Under Water Plot",
        xaxis_title="Date",
        yaxis_title="Drawdown",
        autosize=True,
        showlegend=False,
        xaxis=dict(
            title="Date",
            range=[filtered_df['Date'].min()-timedelta(days=10), filtered_df['Date'].max()+timedelta(days=10)]  # Ensure full date range is visible
        )
    )
        
    year_drawdown_fig = go.Figure()
    year_drawdown_fig.add_trace(go.Scatter(
        x=df.loc[df['Date'].dt.year==latest_year,'Date'], 
        y=df.loc[df['Date'].dt.year==latest_year,'Drawdown'].round(4)*100,
        mode='lines',
        fill='tozeroy',
        line=dict(color='blue'),
        name="Under Water Plot"
    ))
    year_drawdown_fig.update_layout(
        title="Under Water Plot ",
        xaxis_title="Date",
        yaxis_title="Drawdown",
        autosize=True,
        showlegend=False,
        xaxis=dict(
            title="Date",
            range=[df.loc[df['Date'].dt.year==latest_year,'Date'].min()-timedelta(days=3), df.loc[df['Date'].dt.year==latest_year,'Date'].max()+timedelta(days=3)]  # Ensure full date range is visible
        )
    )


    colors_daily_Ret = ["green" if val >= 0 else "red" for val in filtered_df['Returns'].iloc[-252*2:].round(4)]
    daily_return_fig = go.Figure()
    daily_return_fig.add_trace(go.Bar(
        x=filtered_df['Date'].iloc[-252*2:], 
        y=filtered_df['Returns'].iloc[-252*2:].round(4)*100,
        marker=dict(color=colors_daily_Ret)
        # name="Moving Average Cross Over"
    ))
    daily_return_fig.update_layout(
        title="Daily Return",
        xaxis_title="Date",
        yaxis_title="Returns",
        autosize=True,
        showlegend=False,
        xaxis=dict(
            title="Date",
            range=[filtered_df['Date'].iloc[-252*2:].min()-timedelta(days=10), filtered_df['Date'].iloc[-252*2:].max()+timedelta(days=10)]  # Ensure full date range is visible
        )#
    )

    monthly_ret['Close']=monthly_ret['Close']*100
    monthly_seasonality_fig=px.box(monthly_ret, x='Month', y='Close', points='all')

    colors_monthly_Ret = ["green" if val >= 0 else "red" for val in monthly_ret['Close'].round(4)]
    monthly_return_fig = go.Figure()
    monthly_return_fig.add_trace(go.Bar(
        x=monthly_ret['Date'], 
        y=monthly_ret['Close'].round(2),
        marker=dict(color=colors_monthly_Ret)
        # name="Moving Average Cross Over"
    ))
    monthly_return_fig.update_layout(
        title="Monthly Return",
        xaxis_title="Date",
        yaxis_title="Returns",
        autosize=True,
        showlegend=False,
        xaxis=dict(
            title="Date",
            range=[monthly_ret['Date'].min(), monthly_ret['Date'].max()]  # Ensure full date range is visible
        )#
    )
    
    

    colors_yearly_Ret = ["green" if val >= 0 else "red" for val in yearly_ret['Close'].round(4)]
    yearly_return_fig = go.Figure()
    yearly_return_fig.add_trace(go.Bar(
        x=yearly_ret['Date'], 
        y=yearly_ret['Close'].round(4)*100,
        marker=dict(color=colors_yearly_Ret)
        # name="Moving Average Cross Over"
    ))
    yearly_return_fig.update_layout(
        title="Yearly Return",
        xaxis_title="Date",
        yaxis_title="Returns",
        autosize=True,
        showlegend=False,
        xaxis=dict(
            title="Date",
            range=[yearly_ret['Date'].min(), yearly_ret['Date'].max()]  # Ensure full date range is visible
        )#
    )


    date=f"Date: {df['Date'].iloc[-1].strftime('%#m/%d/%y')}"
    ytd_date=f"YTD Day: {df['Day'].iloc[-1]}"
    close=f"Close: {df['Close'].iloc[-1]:.2f}"
    today_ret=f"Today Return: {100 * df['Returns'].iloc[-1]:.2f}%"
    vix_bucket=f"VIX Bucket: {df['VIX'].iloc[-1]:.0f}"
    latest_vix=f"VIX: {df['^VIX'].iloc[-1]:.2f}"
    latest_vix_3mo=f"VIX 3M: {df['^VIX3M'].iloc[-1]:.2f}"
    vix_3mo_0mo=f"VIX 3M/0M: {df['3M_0M_VIX'].iloc[-1]:.3f}"
    drawdown=f"Drawdown: {100 * df['Drawdown'].iloc[-1]:.2f}%"
    return_5d=f"5D Return: {100 * df['5D_Ret'].iloc[-1]:.2f}%"
    return_10d=f"10D Return: {100 * df['10D_Ret'].iloc[-1]:.2f}%"
    return_21d=f"21D Return: {100 * df['21D_Ret'].iloc[-1]:.2f}%"
    return_1yr=f"1yr Return: {100 * df['252D_Ret'].iloc[-1]:.2f}%"
    return_200dma=f"200D PCT: {100 * df['DIST_200MA'].iloc[-1]:.2f}%"
    total_frame = total_frame.applymap(lambda x: round(x, 2) if isinstance(x, (int, float)) else x)
    forecast_return=f"Exp Ret (1mo): {analysis[analysis.columns[0]]['21_Returns']:.2f}%"
    forecast_positive=f"Exp Pos Ret (1mo): {analysis[analysis.columns[0]]['21_Positive Return']:.2f}%"
    forecast_negative=f"Exp Neg Ret (1mo): {analysis[analysis.columns[0]]['21_Negative Return']:.2f}%"

    forecast_level=f"Forecast (1mo): {(1+analysis[analysis.columns[0]]['21_Returns']/ 100)  * analysis[analysis.columns[0]]['Latest']:.2f}"
    forecast_positive_level=f"Pos Forecast (1mo): {(1+analysis[analysis.columns[0]]['21_Positive Return']/ 100)  * analysis[analysis.columns[0]]['Latest'] :.2f}"
    forecast_negative_level=f"Neg Forecast (1mo): {(1+analysis[analysis.columns[0]]['21_Negative Return']/ 100)  * analysis[analysis.columns[0]]['Latest']:.2f}"


#TODO YTD DRAWDOWN filters
# TODO tell soem stories or facts. seasonal trends, correction bear averages
# TODO RSI, some technical indicators
# TODO VaR
# TODO seasonal trends, like month averages
    return [
        date,
        ytd_date,
        close,
        today_ret,
        vix_bucket,
        latest_vix,
        latest_vix_3mo,
        vix_3mo_0mo,
        drawdown,
        return_5d,
        return_10d,
        return_21d,
        return_1yr,
        return_200dma,
        forecast_negative,
        forecast_return,
        forecast_positive,
        forecast_negative_level,
        forecast_level,
        forecast_positive_level,
        price_fig,
        ma_cross_fig,
        dist_200MA_fig,
        daily_return_fig,
        vix_fig,
        short_mid_vix_fig,
        vix_seasonality_fig,
        correlation_fig,
        seasonal_fig,
        ytd_fig,
        drawdown_fig,
        year_drawdown_fig,
        monthly_seasonality_fig,
        total_frame.to_dict('records'),
        monthly_return_fig,
        yearly_return_fig
        
    ]
