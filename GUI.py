# Version 1.0.9
import json
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from datetime import datetime as dt
import pandas as pd
import plotly.graph_objects as go

# import function to call data from Alex' SQLHandler
import SQLHandler as sql_handler
#sql_handler.deleteAllUsers()

#import function to optimize portfolio from Marcl's OptimizeProcedure
import User as u

# preload all stock data (from local PostgreSQL) into df's: [0: Name, 1: ISIN, 2: Index]
#Germany: Frankfurt
df_DAX30 = sql_handler.findComp('DAX30', 'Index', ['Name', 'ISIN', 'Index'], 'companies')
df_DAX30.columns = ['Name', 'ISIN', 'Index']
#Netherlands: Amsterdam
df_AEX = sql_handler.findComp('AEX', 'Index', ['Name', 'ISIN', 'Index'], 'companies')
df_AEX.columns = ['Name', 'ISIN', 'Index']
#France: Paris
df_CAC40 = sql_handler.findComp('CAC40', 'Index', ['Name', 'ISIN', 'Index'], 'companies')
df_CAC40.columns = ['Name', 'ISIN', 'Index']
#Spain: Madrid
df_IBEX35 = sql_handler.findComp('IBEX35', 'Index', ['Name', 'ISIN', 'Index'], 'companies')
df_IBEX35.columns = ['Name', 'ISIN', 'Index']
#UK: London
df_FTSE100 = sql_handler.findComp('FTSE100', 'Index', ['Name', 'ISIN', 'Index'], 'companies')
df_FTSE100.columns = ['Name', 'ISIN', 'Index']
#USA: New York
df_SP1500 = sql_handler.findComp('SP1500', 'Index', ['Name', 'ISIN', 'Index'], 'companies')
df_SP1500.columns = ['Name', 'ISIN', 'Index']
#Japan: Tokio
df_NIKKEI300 = sql_handler.findComp('Nikkei300', 'Index', ['Name', 'ISIN', 'Index'], 'companies')
df_NIKKEI300.columns = ['Name', 'ISIN', 'Index']
#Hongkong
df_HSI = sql_handler.findComp('HSI', 'Index', ['Name', 'ISIN', 'Index'], 'companies') #alles in CAPS bald
df_HSI.columns = ['Name', 'ISIN', 'Index']
#China: Shenzhen
df_SZSE = sql_handler.findComp('SZSE', 'Index', ['Name', 'ISIN', 'Index'], 'companies')
df_SZSE.columns = ['Name', 'ISIN', 'Index']


# set up options for asset mix - cut df's and create dictionary for all options
# make DAX30 df to dict: d_DAX30
df_ = df_DAX30.drop(df_DAX30.columns[[1,2]], axis=1)
df_.rename(columns={'Name': 'DAX30'}, inplace=True)
d_Dax30 = df_.to_dict('list')

# make AEX df to dict: d_AEX
df_ = df_AEX.drop(df_AEX.columns[[1,2]], axis=1)
df_.rename(columns={'Name': 'AEX'}, inplace=True)
d_AEX = df_.to_dict('list')

# make CAC40 df to dict: d_CAC40
df_ = df_CAC40.drop(df_CAC40.columns[[1,2]], axis=1)
df_.rename(columns={'Name': 'CAC40'}, inplace=True)
d_CAC40 = df_.to_dict('list')

# make IBEX35 df to dict: d_IBEX35
df_ = df_IBEX35.drop(df_IBEX35.columns[[1,2]], axis=1)
df_.rename(columns={'Name': 'IBEX35'}, inplace=True)
d_IBEX35 = df_.to_dict('list')

# make FTSE100 df to dict: d_FTSE100
df_ = df_FTSE100.drop(df_FTSE100.columns[[1,2]], axis=1)
df_.rename(columns={'Name': 'FTSE100'}, inplace=True)
d_FTSE100 = df_.to_dict('list')

# make SP1500 df to dict: d_SP1500
df_ = df_SP1500.drop(df_SP1500.columns[[1,2]], axis=1)
df_.rename(columns={'Name': 'SP1500'}, inplace=True)
d_SP1500 = df_.to_dict('list')

# make NIKKEI300 df to dict: d_NIKKEI300
df_ = df_NIKKEI300.drop(df_NIKKEI300.columns[[1,2]], axis=1)
df_.rename(columns={'Name': 'NIKKEI300'}, inplace=True)
d_NIKKEI300 = df_.to_dict('list')

# make HSI df to dict: d_HSI
df_ = df_HSI.drop(df_HSI.columns[[1,2]], axis=1)
df_.rename(columns={'Name': 'HSI'}, inplace=True)
d_HSI = df_.to_dict('list')

# make SZSE df to dict: d_SZSE
df_ = df_SZSE.drop(df_SZSE.columns[[1,2]], axis=1)
df_.rename(columns={'Name': 'SZSE'}, inplace=True)
d_SZSE = df_.to_dict('list')

# concatenate all dicts to one: all_stock_options
all_stock_options = dict(d_Dax30, **d_AEX , **d_CAC40, **d_IBEX35, **d_FTSE100, **d_SP1500, **d_NIKKEI300,**d_HSI, **d_SZSE)

#print('df_DAX30:\n', df_DAX30.head(), '\n')
#print('ADIDAS ISIN:', df_DAX30.loc[df_DAX30['Name'] == 'ADIDAS'].iloc[0]['ISIN'])

# set up app and design style
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# server = app.server - may be implemented at a later stage

#set up initial layout to be displayed
app.layout = html.Div([

    ###HEADER###
    html.Div([

        ##HEADER##
        html.H3(children='Markowitz Portfolio Optimizer',
                style={'textAlign': 'center'}
                ),

        ##SUBHEADER##
        html.Div(children='''
           A web application by A. Rank, M. Perez and J. Madler
           ''',
                 style={'textAlign': 'center'}
                 ),

        ##DIVIDER##
        html.Hr(style={
            'width': '90%'}
        )

    ]),

    ###LEFT BOX (INPUT)###
    html.Div([

        ##INPUT 1: 'portfolio_name_input'
        html.Div([
            html.Div([
                dcc.Markdown('''
                **User name:**
                ''')
            ], style={
                'width': '30%',
                'float': 'left',
                'display': 'table-cell',
                'verticalAlign': 'middle'
            }),

            html.Div([
                dcc.Input(id='portfolio_name_input',
                          type='text',
                          placeholder='Max Mustermann',
                          )
            ], style={
                'width': '50%',
                'float': 'right',
                'display': 'table-cell',
                'verticalAlign': 'middle'
            })
        ], style={
            'width': '100%',
            'display': 'table',
            'verticalAlign': 'middle'
        }),

        html.Hr(style={
            'width': '99%',
            'display': 'inline-block'
        }),

        ##INPUT 2: 'portfolio_amount_input'
        html.Div([
            html.Div([
                dcc.Markdown('''
                    **Amount (EUR):**
                    ''')
            ], style={
                'width': '30%',
                'float': 'left',
                'display': 'table-cell',
                'verticalAlign': 'middle'
            }),

            html.Div([
                dcc.Input(id='portfolio_amount_input',
                          type='number',
                          min=0,
                          step=10,
                          value=1000,
                          )
            ], style={
                'width': '50%',
                'float': 'right',
                'display': 'table-cell',
                'verticalAlign': 'middle'
            })
        ], style={
            'width': '100%',
            'display': 'table',
            'verticalAlign': 'middle'
        }),

        html.Hr(style={
            'width': '99%',
            'display': 'inline-block'
        }),

        ##INPUT 3: 'portfolio_risk_input'
        html.Div([
            html.Div([
                dcc.Markdown('''
                **Optimization objective:**
                ''')
            ], style={
                'width': '30%',
                'float': 'left',
                'display': 'table-cell',
                'verticalAlign': 'middle'
            }),
            html.Div([
                dcc.Slider(id='portfolio_risk_input',
                       min=0,
                       max=2,
                       marks={
                           0: 'volatility',
                           1: 'sharpe ratio',
                           2: 'return'
                       },
                       value=1
            )], style={
                'width': '50%',
                'float': 'right',
                'display': 'table-cell',
                'verticalAlign': 'middle'
            }),
        ], style={
            'width': '100%',
            'display': 'table',
            'verticalAlign': 'middle'
        }),

        html.Hr(style={
            'width': '99%',
            'display': 'inline-block'
        }),

        ##INPUT 4: 'portfolio_assets_input'
        html.Div([
            html.Div([
                dcc.Markdown('''
                **Asset mix:**
                ''')
            ]),
            html.Div([
                html.Div([
                    dcc.Checklist(id='portfolio_asset_DAX30_activate',
                                  options=[{'label': 'DAX30', 'value': 'DAX30'}])
                ], style={
                    'width': '30%',
                    'float': 'left',
                    'display': 'table-cell',
                    'verticalAlign': 'middle',
                    'horizontalAlign': 'middle'
                }),
                html.Div([
                    dcc.Dropdown(id='portfolio_asset_DAX30_input',
                                 # options will be filled by callback
                                 multi=True)
                ], style={
                    'width': '50%',
                    'float': 'right',
                    'display': 'table-cell',
                    'verticalAlign': 'middle',
                    'horizontalAlign': 'middle',
                })
            ], style={
                'width': '100%',
                'display': 'table',
                'verticalAlign': 'middle',
                'margin': {'t': 10, 'b': 10}
            }),

            html.Div([
                html.Div([
                    dcc.Checklist(id='portfolio_asset_AEX_activate',
                                  options=[{'label': 'AEX', 'value': 'AEX'}])
                ], style={
                    'width': '30%',
                    'float': 'left',
                    'display': 'table-cell',
                    'verticalAlign': 'middle',
                    'horizontalAlign': 'middle'
                }),
                html.Div([
                    dcc.Dropdown(id='portfolio_asset_AEX_input',
                                 # options will be filled by callback
                                 multi=True)
                ], style={
                    'width': '50%',
                    'float': 'right',
                    'display': 'table-cell',
                    'verticalAlign': 'middle',
                    'horizontalAlign': 'middle',
                })
            ], style={
                'width': '100%',
                'display': 'table',
                'verticalAlign': 'middle',
                'margin': {'t': 10, 'b': 10}
            }),

            html.Div([
                html.Div([
                    dcc.Checklist(id='portfolio_asset_CAC40_activate',
                                  options=[{'label': 'CAC40', 'value': 'CAC40'}])
                ], style={
                    'width': '30%',
                    'float': 'left',
                    'display': 'table-cell',
                    'verticalAlign': 'middle',
                    'horizontalAlign': 'middle'
                }),
                html.Div([
                    dcc.Dropdown(id='portfolio_asset_CAC40_input',
                                 # options will be filled by callback
                                 multi=True)
                ], style={
                    'width': '50%',
                    'float': 'right',
                    'display': 'table-cell',
                    'verticalAlign': 'middle',
                    'horizontalAlign': 'middle'
                })
            ], style={
                'width': '100%',
                'display': 'table',
                'verticalAlign': 'middle'
            }),

            html.Div([
                html.Div([
                    dcc.Checklist(id='portfolio_asset_IBEX35_activate',
                                  options=[{'label': 'IBEX35', 'value': 'IBEX35'}])
                ], style={
                    'width': '30%',
                    'float': 'left',
                    'display': 'table-cell',
                    'verticalAlign': 'middle',
                    'horizontalAlign': 'middle'
                }),
                html.Div([
                    dcc.Dropdown(id='portfolio_asset_IBEX35_input',
                                 # options will be filled by callback
                                 multi=True)
                ], style={
                    'width': '50%',
                    'float': 'right',
                    'display': 'table-cell',
                    'verticalAlign': 'middle',
                    'horizontalAlign': 'middle'
                })
            ], style={
                'width': '100%',
                'display': 'table',
                'verticalAlign': 'middle'
            }),

            html.Div([
                html.Div([
                    dcc.Checklist(id='portfolio_asset_FTSE100_activate',
                                  options=[{'label': 'FTSE100', 'value': 'FTSE100'}])
                ], style={
                    'width': '30%',
                    'float': 'left',
                    'display': 'table-cell',
                    'verticalAlign': 'middle',
                    'horizontalAlign': 'middle'
                }),
                html.Div([
                    dcc.Dropdown(id='portfolio_asset_FTSE100_input',
                                 # options will be filled by callback
                                 multi=True)
                ], style={
                    'width': '50%',
                    'float': 'right',
                    'display': 'table-cell',
                    'verticalAlign': 'middle',
                    'horizontalAlign': 'middle'
                })
            ], style={
                'width': '100%',
                'display': 'table',
                'verticalAlign': 'middle'
            }),

            html.Div([
                html.Div([
                    dcc.Checklist(id='portfolio_asset_SP1500_activate',
                                  options=[{'label': 'S&P1500', 'value': 'SP1500'}])
                ], style={
                    'width': '30%',
                    'float': 'left',
                    'display': 'table-cell',
                    'verticalAlign': 'middle',
                    'horizontalAlign': 'middle'
                }),
                html.Div([
                    dcc.Dropdown(id='portfolio_asset_SP1500_input',
                                 # options will be filled by callback
                                 multi=True)
                ], style={
                    'width': '50%',
                    'float': 'right',
                    'display': 'table-cell',
                    'verticalAlign': 'middle',
                    'horizontalAlign': 'middle'
                })
            ], style={
                'width': '100%',
                'display': 'table',
                'verticalAlign': 'middle'
            }),

            html.Div([
                html.Div([
                    dcc.Checklist(id='portfolio_asset_NIKKEI300_activate',
                                  options=[{'label': 'NIKKEI300', 'value': 'NIKKEI300'}])
                ], style={
                    'width': '30%',
                    'float': 'left',
                    'display': 'table-cell',
                    'verticalAlign': 'middle',
                    'horizontalAlign': 'middle'
                }),
                html.Div([
                    dcc.Dropdown(id='portfolio_asset_NIKKEI300_input',
                                 # options will be filled by callback
                                 multi=True)
                ], style={
                    'width': '50%',
                    'float': 'right',
                    'display': 'table-cell',
                    'verticalAlign': 'middle',
                    'horizontalAlign': 'middle'
                })
            ], style={
                'width': '100%',
                'display': 'table',
                'verticalAlign': 'middle'
            }),

            html.Div([
                html.Div([
                    dcc.Checklist(id='portfolio_asset_HSI_activate',
                                  options=[{'label': 'HSI', 'value': 'HSI'}])
                ], style={
                    'width': '30%',
                    'float': 'left',
                    'display': 'table-cell',
                    'verticalAlign': 'middle',
                    'horizontalAlign': 'middle'
                }),
                html.Div([
                    dcc.Dropdown(id='portfolio_asset_HSI_input',
                                 # options will be filled by callback
                                 multi=True)
                ], style={
                    'width': '50%',
                    'float': 'right',
                    'display': 'table-cell',
                    'verticalAlign': 'middle',
                    'horizontalAlign': 'middle'
                })
            ], style={
                'width': '100%',
                'display': 'table',
                'verticalAlign': 'middle'
            }),
            html.Div([
                html.Div([
                    dcc.Checklist(id='portfolio_asset_SZSE_activate',
                                  options=[{'label': 'SZSE', 'value': 'SZSE'}])
                ], style={
                    'width': '30%',
                    'float': 'left',
                    'display': 'table-cell',
                    'verticalAlign': 'middle',
                    'horizontalAlign': 'middle'
                }),
                html.Div([
                    dcc.Dropdown(id='portfolio_asset_SZSE_input',
                                 # options will be filled by callback
                                 multi=True)
                ], style={
                    'width': '50%',
                    'float': 'right',
                    'display': 'table-cell',
                    'verticalAlign': 'middle',
                    'horizontalAlign': 'middle'
                })
            ], style={
                'width': '100%',
                'display': 'table',
                'verticalAlign': 'middle'
            })
        ]),

        html.Hr(style={
            'width': '99%',
            'display': 'inline-block'
        }),

        ##INPUT 5: 'portfolio_broker_fix_input', 'portfolio_broker_var_input'
        html.Div([
            html.Div([
                dcc.Markdown('''
                    **Broker fees (EUR and %):**
                    ''')
            ], style={
                'width': '30%',
                'float': 'left',
                'display': 'table-cell',
                'verticalAlign': 'middle'
            }),

            html.Div([
                html.Div([
                    html.Div([
                        dcc.Input(id='portfolio_broker_fix_input',
                                  type='number',
                                  min=0,
                                  max=100,
                                  step=0.1,
                                  placeholder='fixed',
                                  )
                    ], style={
                        'width': '45%',
                        'float': 'left',
                        'display': 'table-cell',
                        'verticalAlign': 'middle'
                    }),
                    html.Div([
                        dcc.Input(id='portfolio_broker_var_input',
                                  type='number',
                                  min=0,
                                  max=100,
                                  step=0.1,
                                  placeholder='variable',
                                  )
                    ], style={
                        'width': '45%',
                        'float': 'right',
                        'display': 'table-cell',
                        'verticalAlign': 'middle'
                    })
                ], style={
                    'width': '100%',
                    'display': 'table',
                    'verticalAlign': 'middle'
                })
            ], style={
                'width': '50%',
                'float': 'right',
                'display': 'table-cell',
                'verticalAlign': 'middle'
            })
        ], style={
            'width': '100%',
            'display': 'table',
            'verticalAlign': 'middle'
        }),

        html.Hr(style={
            'width': '99%',
            'display': 'inline-block'
        }),

        html.Hr(style={
            'width': '99%',
            'display': 'inline-block'
        }),

        ##Input 7: 'portfolio_time_period_input'
        html.Div([
            html.Div([
                dcc.Markdown('''
                    **Data time period:**
                    ''')
            ]),

            html.Div([
                html.Div([
                    dcc.Markdown('''
                        Start Date:
                        ''')
                ], style={
                    'width': '50%',
                    'float': 'left',
                    'display': 'table-cell',
                    'verticalAlign': 'middle'
                }),
                html.Div([
                    #7.1: 'portfolio_time_period_start_input'
                    dcc.DatePickerSingle(
                        id='portfolio_time_period_start_input',
                        date=dt(2015, 1, 1),
                        min_date_allowed=dt(1990, 1, 1),
                        max_date_allowed=dt(2019, 9, 1),
                        display_format='DD/MM/YYYY',
                        with_portal=True
                    )
                ], style={
                    'width': '50%',
                    'float': 'right',
                    'display': 'table-cell',
                    'verticalAlign': 'middle'
                })
            ], style={
                'width': '100%',
                'display': 'table',
                'verticalAlign': 'middle'
            }),

            html.Div([
                html.Div([
                    dcc.Markdown('''
                        End Date:
                        ''')
                ], style={
                    'width': '50%',
                    'float': 'left',
                    'display': 'table-cell',
                    'verticalAlign': 'middle'
                }),
                html.Div([
                    #7.2: 'portfolio_time_period_end_input'
                    dcc.DatePickerSingle(
                        id='portfolio_time_period_end_input',
                        date=dt(2017, 1, 1),
                        min_date_allowed=dt(1991, 1, 1),
                        max_date_allowed=dt(2019, 9, 1),
                        display_format='DD/MM/YYYY',
                        with_portal=True
                    )
                ], style={
                    'width': '50%',
                    'float': 'right',
                    'display': 'table-cell',
                    'verticalAlign': 'middle'
                })
            ], style={
                'width': '100%',
                'display': 'table',
                'verticalAlign': 'middle'
            })

        ], style={
            'width': '100%',
            'display': 'table',
            'verticalAlign': 'middle'
        }),

        html.Div([
            html.Div([
                #markdown
                dcc.Markdown('''
                **Time Interval:**
                ''')
            ], style={
                    'width': '50%',
                    'float': 'left',
                    'display': 'table-cell',
                    'verticalAlign': 'middle'
                }),

            html.Div([
                ##INPUT 7.3: 'portfolio_time_period_interval_input'
                dcc.Slider(id='portfolio_time_period_interval_input',
                           min=0,
                           max=1,
                           marks={
                               0: 'Monthly',
                               1: 'Daily',
                           },
                           value=0)
            ], style={
                    'width': '50%',
                    'float': 'right',
                    'display': 'table-cell',
                    'verticalAlign': 'middle'
                })

        ], style={
            'width': '100%',
            'display': 'table',
            'verticalAlign': 'middle',
            'marginTop': '25px'
        }),

        html.Hr(style={
            'width': '99%',
            'display': 'inline-block'
        }),


        html.Div([

            ##INPUT 8: 'portfolio_creation_button_input'
            html.Div([
                html.Button(
                    id='portfolio_creation_button_input',
                    children='Create Portfolio',
                )
            ], style={
                'width': '50%',
                'float': 'left',
                'display': 'table-cell',
                'verticalAlign': 'middle'
            }),

            ##INPUT 9: 'portfolio_loading_button_input'
            html.Div([
                html.Button(
                    id='portfolio_loading_button_input',
                    children='Load My Portfolio',
                )
            ], style={
                'width': '50%',
                'float': 'right',
                'display': 'table-cell',
                'verticalAlign': 'middle'
            })
        ], style={
            'width': '99%',
            'display': 'table',
            'verticalAlign': 'middle'
        }),

        html.Hr(style={
            'width': '99%',
            'display': 'inline-block'
        }),

        html.Div(
            ##OUTPUT 7: 'portfolio_rebalance_popup_container': hidden by default
            id='portfolio_rebalance_popup_container',
            style={
                'display': 'none' #will be set to 'block' (activated) in callback
            },
            children=[
                html.Div([
                    dcc.Markdown(
                        '''
                        **Portfolio Rebalancing:**
                        ''')
                ]),
                html.Div([
                    html.Div([
                        dcc.Markdown(
                            '''
                New End Date:
                ''')
                    ], style={
                        'width': '50%',
                        'float': 'left',
                        'display': 'table-cell',
                        'verticalAlign': 'middle'
                    }),

                    html.Div([
                        ##INPUT 10: 'portfolio_rebalance_end_date_input'
                        dcc.DatePickerSingle(
                            id='portfolio_rebalance_end_date_input',
                            date=dt(2019, 1, 1),
                            min_date_allowed=dt(1991, 1, 1),
                            max_date_allowed=dt(2019, 9, 1),
                            display_format='DD/MM/YYYY',
                            with_portal=True,
                        )
                    ], style={
                        'width': '50%',
                        'float': 'right',
                        'display': 'table-cell',
                        'verticalAlign': 'middle'
                    })
                ], style={
                    'width': '100%',
                    'display': 'table',
                    'verticalAlign': 'middle'
                }),
                html.Div([
                    ##INPUT 11: 'portfolio_rebalance_button_input'
                    html.Button(
                        id='portfolio_rebalance_button_input',
                        children='Rebalance Portfolio',
                    )
                ], style={
                    'float': 'left',
                    'verticalAlign': 'middle',
                    'marginTop': '20px'
                })
            ])
    ], style={
        'borderBottom': 'thin lightgrey solid',
        'backgroundColor': '#fafafa',
        'padding': '15px 5px',
        'width': '34%',
        'display': 'inline-block'
    }),

    ###RIGHT BOX (OUTPUT)###
    html.Div([

        ##OUTPUT 1: 'portfolio_name_output'
        html.Div([
            html.H4(
                id='portfolio_name_output',
                children='',
                style={
                     'verticalAlign': 'middle',
                     'textAlign': 'center'
                 }
            )
        ]),

        html.Hr(style={
            'width': '99%',
            'display': 'inline-block'
        }),

        html.Div([
            ##OUTPUT 2: 'portfolio_sharpe_ratio_output'
            html.Div(
                id='portfolio_sharpe_ratio_output',
                style={
                    'width': '45%',
                    'float': 'left',
                    'display': 'table-cell',
                    'verticalAlign': 'middle'
                }
            ),
            ##OUTPUT 3: 'portfolio_return_output'
            html.Div(
                id='portfolio_return_output',
                style={
                    'width': '20%',
                    'float': 'middle',
                    'display': 'table-cell',
                    'verticalAlign': 'middle'
                }
            ),
            ##OUTPUT 3: 'portfolio_std_output'
            html.Div(
                id='portfolio_std_output',
                style={
                    'width': '45%',
                    'float': 'right',
                    'display': 'table-cell',
                    'verticalAlign': 'middle'
                }
            )
        ], style={
            'width': '99%',
            'display': 'table',
            'verticalAlign': 'middle'
        }),

        html.Hr(style={
            'width': '99%',
            'display': 'inline-block'
        }),

        ##OUTPUT 5: 'portfolio_graph_output'
        html.Div([
            dcc.Graph(id='portfolio_graph_output')
        ]),


        #html.Hr(style={
        #    'width': '99%',
        #    'display': 'inline-block'
        #}),

        ##OUTPUT 6: 'portfolio_table_output'
        html.Div([
            dash_table.DataTable(
                id='portfolio_table_output',
                style_as_list_view=True,
                style_header={
                    'backgroundColor': '#f4f4f4',
                    'fontWeight': 'bold'
                },
                style_cell={'textAlign': 'left',
                            'padding': '5px',
                            'fontSize':14,
                            'font-family': 'sans-serif'}
            )
        ])

    ], style={
        'borderBottom': 'thin lightgrey solid',
        'backgroundColor': '#f4f4f4',
        'padding': '15px 5px',
        'width': '64%',
        'display': 'inline-block',
        'float': 'right'
    })

])


# set up GUI interactivity (callbacks)
#INPUTS:
#1:     'portfolio_name_input'
#2:     'portfolio_amount_input'
#3:     'portfolio_risk_input'
#4.1.1: 'portfolio_asset_DAX30_activate'
#4.1.2: 'portfolio_asset_DAX30_input'
#4.2.1: 'portfolio_asset_AEX_activate'
#4.2.2: 'portfolio_asset_AEX_input'
#4.3.1: 'portfolio_asset_CAC40_activate'
#4.3.2: 'portfolio_asset_CAC40_input'
#4.4.1: 'portfolio_asset_IBEX35_activate'
#4.4.2: 'portfolio_asset_IBEX35_input'
#4.5.1: 'portfolio_asset_FTSE100_activate'
#4.5.2: 'portfolio_asset_FTSE100_input'
#4.6.1: 'portfolio_asset_SP1500_activate'
#4.6.2: 'portfolio_asset_SP1500_input'
#4.7.1: 'portfolio_asset_NIKKEI300_activate'
#4.7.2: 'portfolio_asset_NIKKEI300_input'
#4.8.1: 'portfolio_asset_HSI_activate'
#4.8.2: 'portfolio_asset_HSI_input'
#4.9.1: 'portfolio_asset_SZSE_activate'
#4.9.2: 'portfolio_asset_SZSE_input'
#5.1:   'portfolio_broker_fix_input'
#5.2:   'portfolio_broker_var_input'
#6.1:   'portfolio_time_period_start_input'
#6.2:   'portfolio_time_period_end_input'
#6.3:   'portfolio_time_period_interval_input'
#7:     'portfolio_creation_button_input'
#8:     'portfolio_loading_button_input'
#9:    'portfolio_rebalance_end_date_input'
#10:    'portfolio_rebalance_button_input'

#OUTPUTS:
#1:     'portfolio_name_output'
#2:     'portfolio_sharpe_ratio_output'
#4:     'portfolio_return_output'
#3:     'portfolio_std_output'
#5:     'portfolio_graph_output'
#6:     'portfolio_table_output'
#7:     'portfolio_rebalance_popup_container'


# activate DAX30 Dropdown menu when DAX30 Checklist is ticked
@app.callback(Output('portfolio_asset_DAX30_input', 'options'),
              [Input('portfolio_asset_DAX30_activate', 'value')])
def set_DAX30_Dropdown(value_DAX30):
#    print('value_DAX30:', value_DAX30)
    if value_DAX30 is not None and value_DAX30:
        return [{'label': i, 'value': i} for i in all_stock_options[value_DAX30[0]]]
    else:
        return [{'label': '', 'value': ''}]
# select all options in DAX_30 when DAX30 Checklist is ticked - #TODO

# activate AEX Dropdown menu when AEX Checklist is ticked
@app.callback(Output('portfolio_asset_AEX_input', 'options'),
              [Input('portfolio_asset_AEX_activate', 'value')])
def set_AEX_Dropdown(value_AEX):
#    print('value_AEX:', value_AEX)
    if value_AEX is not None and value_AEX:
        return [{'label': i, 'value': i} for i in all_stock_options[value_AEX[0]]]
    else:
        return [{'label': '', 'value': ''}]
# select all options in AEX when AEX Checklist is ticked - #TODO

# activate CAC40 Dropdown menu when CAC40 Checklist is ticked
@app.callback(Output('portfolio_asset_CAC40_input', 'options'),
              [Input('portfolio_asset_CAC40_activate', 'value')])
def set_CAC40_Dropdown(value_CAC40):
    if value_CAC40 is not None and value_CAC40:
        return [{'label': i, 'value': i} for i in all_stock_options[value_CAC40[0]]]
    else:
        return [{'label': '', 'value': ''}]
# select all options in CAC_40 when CAC40 Checklist is ticked - #TODO

# activate IBEX35 Dropdown menu when IBEX35 Checklist is ticked
@app.callback(Output('portfolio_asset_IBEX35_input', 'options'),
              [Input('portfolio_asset_IBEX35_activate', 'value')])
def set_IBEX35_Dropdown(value_IBEX35):
    if value_IBEX35 is not None and value_IBEX35:
        return [{'label': i, 'value': i} for i in all_stock_options[value_IBEX35[0]]]
    else:
        return [{'label': '', 'value': ''}]
# select all options in IBEX_35 when IBEX35 Checklist is ticked - #TODO

# activate FTSE100 Dropdown menu when FTSE100 Checklist is ticked
@app.callback(Output('portfolio_asset_FTSE100_input', 'options'),
              [Input('portfolio_asset_FTSE100_activate', 'value')])
def set_FTSE100_Dropdown(value_FTSE100):
    if value_FTSE100 is not None and value_FTSE100:
        return [{'label': i, 'value': i} for i in all_stock_options[value_FTSE100[0]]]
    else:
        return [{'label': '', 'value': ''}]
# select all options in FTSE_100 when FTSE100 Checklist is ticked - #TODO

# activate SP1500 Dropdown menu when SP1500 Checklist is ticked
@app.callback(Output('portfolio_asset_SP1500_input', 'options'),
              [Input('portfolio_asset_SP1500_activate', 'value')])
def set_SP1500_Dropdown(value_SP1500):
    if value_SP1500 is not None and value_SP1500:
        return [{'label': i, 'value': i} for i in all_stock_options[value_SP1500[0]]]
    else:
        return [{'label': '', 'value': ''}]
# select all options in SP1500 when SP1500 Checklist is ticked - #TODO

# activate NIKKEI300 Dropdown menu when NIKKEI300 Checklist is ticked
@app.callback(Output('portfolio_asset_NIKKEI300_input', 'options'),
              [Input('portfolio_asset_NIKKEI300_activate', 'value')])
def set_NIKKEI300_Dropdown(value_NIKKEI300):
    if value_NIKKEI300 is not None and value_NIKKEI300:
        return [{'label': i, 'value': i} for i in all_stock_options[value_NIKKEI300[0]]]
    else:
        return [{'label': '', 'value': ''}]
# select all options in NIKKEI300 when NIKKEI300 Checklist is ticked - #TODO

# activate HSI Dropdown menu when HSI Checklist is ticked
@app.callback(Output('portfolio_asset_HSI_input', 'options'),
              [Input('portfolio_asset_HSI_activate', 'value')])
def set_HSI_Dropdown(value_HSI):
    if value_HSI is not None and value_HSI:
        return [{'label': i, 'value': i} for i in all_stock_options[value_HSI[0]]]
    else:
        return [{'label': '', 'value': ''}]
# select all options in HSI when HSI Checklist is ticked - #TODO

# activate SZSE Dropdown menu when SZSE Checklist is ticked
@app.callback(Output('portfolio_asset_SZSE_input', 'options'),
              [Input('portfolio_asset_SZSE_activate', 'value')])
def set_SZSE_Dropdown(value_SZSE):
    if value_SZSE is not None and value_SZSE:
        return [{'label': i, 'value': i} for i in all_stock_options[value_SZSE[0]]]
    else:
        return [{'label': '', 'value': ''}]
# select all options in SZSE when SZSE Checklist is ticked - #TODO

###DEF 1: create_load_rebalance_portfolio
@app.callback([Output('portfolio_name_output', 'children'),
               Output('portfolio_sharpe_ratio_output', 'children'),
               Output('portfolio_return_output', 'children'),
               Output('portfolio_std_output', 'children'),
               Output('portfolio_table_output', 'data'),
               Output('portfolio_table_output', 'columns'),
               Output('portfolio_rebalance_popup_container', 'style'),
               Output('portfolio_graph_output', 'figure')],
              [Input('portfolio_creation_button_input', 'n_clicks'),
               Input('portfolio_loading_button_input', 'n_clicks'),
               Input('portfolio_rebalance_button_input', 'n_clicks')],
              [State('portfolio_name_input', 'value'),
               State('portfolio_amount_input', 'value'),
               State('portfolio_risk_input', 'value'),
               State('portfolio_asset_DAX30_input', 'value'),
               State('portfolio_asset_AEX_input', 'value'),
               State('portfolio_asset_CAC40_input', 'value'),
               State('portfolio_asset_IBEX35_input', 'value'),
               State('portfolio_asset_FTSE100_input', 'value'),
               State('portfolio_asset_SP1500_input', 'value'),
               State('portfolio_asset_NIKKEI300_input', 'value'),
               State('portfolio_asset_HSI_input', 'value'),
               State('portfolio_asset_SZSE_input', 'value'),
               State('portfolio_broker_fix_input', 'value'),
               State('portfolio_broker_var_input', 'value'),
               State('portfolio_time_period_start_input', 'date'),
               State('portfolio_time_period_end_input', 'date'),
               State('portfolio_time_period_interval_input', 'value'),
               State('portfolio_rebalance_end_date_input', 'date')])
def create_load_rebalance_portfolio(n_clicks_create,
                                    n_clicks_load,
                                    n_clicks_rebalance,
                                    portfolio_name_input,
                                    portfolio_amount_input,
                                    portfolio_risk_input,
                                    portfolio_asset_DAX30_input,
                                    portfolio_asset_AEX_input,
                                    portfolio_asset_CAC40_input,
                                    portfolio_asset_IBEX35_input,
                                    portfolio_asset_FTSE100_input,
                                    portfolio_asset_SP1500_input,
                                    portfolio_asset_NIKKEI300_input,
                                    portfolio_asset_HSI_input,
                                    portfolio_asset_SZSE_input,
                                    portfolio_broker_fix_input,
                                    portfolio_broker_var_input,
                                    portfolio_time_period_start_input,
                                    portfolio_time_period_end_input,
                                    portfolio_time_period_interval_input,
                                    portfolio_time_period_rebalance_input):

    ctx = dash.callback_context
    ctx_msg = json.dumps({
        #'states': ctx.states,
        'inputs': ctx.inputs,
        'triggered': ctx.triggered
    }, indent=2)

    if not ctx.triggered:
        raise PreventUpdate
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    ##portfolio_creation_button_input pressed: create new portfolio
    if button_id == 'portfolio_creation_button_input':
        if portfolio_name_input is None or portfolio_amount_input is None:
            raise PreventUpdate

        #stop if username (id) already exists
        if sql_handler.exists(portfolio_name_input):
            print('MESSAGE: Portfolio could not be created. Username already exists. Please enter another Username.')
            raise PreventUpdate

        #prepare input for optimization procedure
        ISIN_list = get_asset_isin_to_name_list(portfolio_asset_DAX30_input,
                                                portfolio_asset_AEX_input,
                                                portfolio_asset_CAC40_input,
                                                portfolio_asset_IBEX35_input,
                                                portfolio_asset_FTSE100_input,
                                                portfolio_asset_SP1500_input,
                                                portfolio_asset_NIKKEI300_input,
                                                portfolio_asset_HSI_input,
                                                portfolio_asset_SZSE_input)

        #if ISIN_list is empty, stop portfolio optimization procedure
        if not ISIN_list:
            raise PreventUpdate

        optimize_objective = get_optimize_objective_char(portfolio_risk_input)
        #start and end dates as string - cutoff timestamps (if not manually entered)
        if len(portfolio_time_period_start_input) > 10:
            period_start = portfolio_time_period_start_input[:-9]
        else:
            period_start = portfolio_time_period_start_input
        if len(portfolio_time_period_end_input) > 10:
            period_end = portfolio_time_period_end_input[:-9]
        else:
            period_end = portfolio_time_period_end_input
        time_interval = get_time_interval_char(portfolio_time_period_interval_input)
        if portfolio_broker_fix_input is not None:
            broker_fix = float(portfolio_broker_fix_input)
        else:
            broker_fix = 0
        if portfolio_broker_var_input is not None:
            broker_var = int(portfolio_broker_var_input)
        else:
            broker_var = 0

        #create user to be optimized
        user = u.User(portfolio_name_input,
                      portfolio_amount_input,
                      ISIN_list,
                      time_interval=time_interval,
                      optimize_objective=optimize_objective,
                      period_start=period_start,
                      broker_fix=broker_fix,
                      broker_var=broker_var)

        #start optimization procedure
        user.optimize_req(period_end=period_end)

        #retrieve & unpack results: #1 displayable output and #2 rebalancing layout
        portfolio_result = get_portfolio_result(user)
        name_children = portfolio_result[0]
        sharpe_children = portfolio_result[1]
        return_children = portfolio_result[2]
        std_children = portfolio_result[3]
        table_data = portfolio_result[4]
        table_columns = portfolio_result[5]
        df_graph = portfolio_result[6]
        graph_figure = portfolio_result[7]
        portfolio_rebalance_popup = {'display': 'block'}

        #save user to local SQL database
        user.portfolio_history = df_graph
        sql_handler.saveUser(user)

        return name_children, \
               sharpe_children, \
               return_children, \
               std_children, \
               table_data, \
               table_columns, \
               portfolio_rebalance_popup,\
               graph_figure

    ##portfolio_loading_button_input pressed: Load user and portfolio
    elif button_id == 'portfolio_loading_button_input' and n_clicks_load is not None:
        if portfolio_name_input is None:
            raise PreventUpdate

        #stop if username (id) does not exist
        if not sql_handler.exists(portfolio_name_input):
            print('MESSAGE: Portfolio could not be loaded. Username does not exist. Please enter another Username.')
            raise PreventUpdate

        # get user from SQL data base
        user = sql_handler.getUser(portfolio_name_input)

        #retrieve & unpack results: #1 displayable output and #2 rebalancing layout
        portfolio_result = get_portfolio_result(user)
        name_children = portfolio_result[0]
        sharpe_children = portfolio_result[1]
        return_children = portfolio_result[2]
        std_children = portfolio_result[3]
        table_data = portfolio_result[4]
        table_columns = portfolio_result[5]
        df_graph = portfolio_result[6]
        graph_figure = portfolio_result[7]
        portfolio_rebalance_popup = {'display': 'block'}

        return name_children, \
               sharpe_children, \
               return_children, \
               std_children, \
               table_data, \
               table_columns, \
               portfolio_rebalance_popup,\
               graph_figure

    ##portfolio_rebalance_button_input pressed: Rebalance current portfolio with new end date
    elif button_id == 'portfolio_rebalance_button_input' and n_clicks_rebalance is not None:
        if portfolio_name_input is None:
            raise PreventUpdate

        #stop if username (id) does not exist
        if not sql_handler.exists(portfolio_name_input):
            print('MESSAGE: Portfolio could not be rebalanced. Username does not exist. Please enter another Username.')
            raise PreventUpdate

        # get user from SQL data base
        user = sql_handler.getUser(portfolio_name_input)
        if len(portfolio_time_period_rebalance_input) > 10:
            period_end = portfolio_time_period_rebalance_input[:-9]
        else:
            period_end = portfolio_time_period_rebalance_input

        #start optimization procedure
        user.optimize_req(period_end=period_end)

        #retrieve & unpack results: #1 displayable output and #2 rebalancing layout
        portfolio_result = get_portfolio_result(user)
        name_children = portfolio_result[0]
        sharpe_children = portfolio_result[1]
        return_children = portfolio_result[2]
        std_children = portfolio_result[3]
        table_data = portfolio_result[4]
        table_columns = portfolio_result[5]
        df_graph = portfolio_result[6]
        graph_figure = portfolio_result[7]
        portfolio_rebalance_popup = {'display': 'block'}

        #save user to local SQL database and override last portfolio_history (df)
        user.portfolio_history = df_graph
        sql_handler.saveUser(user)

        return name_children, \
               sharpe_children, \
               return_children, \
               std_children, \
               table_data, \
               table_columns, \
               portfolio_rebalance_popup,\
               graph_figure

    #initial state: no button pressed
    raise PreventUpdate


### Helper-Functions
def update_portfolio_name(portfolio_name_input):
        return '''{}'''.format(portfolio_name_input)

def get_asset_isin_to_name_list(portfolio_asset_DAX30_input,
                                portfolio_asset_AEX_input,
                                portfolio_asset_CAC40_input,
                                portfolio_asset_IBEX35_input,
                                portfolio_asset_FTSE100_input,
                                portfolio_asset_SP1500_input,
                                portfolio_asset_NIKKEI300_input,
                                portfolio_asset_HSI_input,
                                portfolio_asset_SZSE_input):
    isin_list = []

    if portfolio_asset_DAX30_input is not None:
        for x in portfolio_asset_DAX30_input:
            if x in df_DAX30.Name.values:
                isin = df_DAX30.loc[df_DAX30['Name'] == x].iloc[0]['ISIN']
                isin_list.append(isin)

    if portfolio_asset_AEX_input is not None:
        for x in portfolio_asset_AEX_input:
            if x in df_AEX.Name.values:
                isin = df_AEX.loc[df_AEX['Name'] == x].iloc[0]['ISIN']
                isin_list.append(isin)

    if portfolio_asset_CAC40_input is not None:
        for x in portfolio_asset_CAC40_input:
            if x in df_CAC40.Name.values:
                isin = df_CAC40.loc[df_CAC40['Name'] == x].iloc[0]['ISIN']
                isin_list.append(isin)

    if portfolio_asset_IBEX35_input is not None:
        for x in portfolio_asset_IBEX35_input:
            if x in df_IBEX35.Name.values:
                isin = df_IBEX35.loc[df_IBEX35['Name'] == x].iloc[0]['ISIN']
                isin_list.append(isin)

    if portfolio_asset_FTSE100_input is not None:
        for x in portfolio_asset_FTSE100_input:
            if x in df_FTSE100.Name.values:
                isin = df_FTSE100.loc[df_FTSE100['Name'] == x].iloc[0]['ISIN']
                isin_list.append(isin)

    if portfolio_asset_SP1500_input is not None:
        for x in portfolio_asset_SP1500_input:
            if x in df_SP1500.Name.values:
                isin = df_SP1500.loc[df_SP1500['Name'] == x].iloc[0]['ISIN']
                isin_list.append(isin)

    if portfolio_asset_NIKKEI300_input is not None:
        for x in portfolio_asset_NIKKEI300_input:
            if x in df_NIKKEI300.Name.values:
                isin = df_NIKKEI300.loc[df_NIKKEI300['Name'] == x].iloc[0]['ISIN']
                isin_list.append(isin)

    if portfolio_asset_HSI_input is not None:
        for x in portfolio_asset_HSI_input:
            if x in df_HSI.Name.values:
                isin = df_HSI.loc[df_HSI['Name'] == x].iloc[0]['ISIN']
                isin_list.append(isin)

    if portfolio_asset_SZSE_input is not None:
        for x in portfolio_asset_SZSE_input:
            if x in df_SZSE.Name.values:
                isin = df_SZSE.loc[df_SZSE['Name'] == x].iloc[0]['ISIN']
                isin_list.append(isin)

    return isin_list

def get_asset_name_to_isin_list(isin):
    name = 'NULL'
    if isin is not None:

       if isin in df_DAX30.ISIN.values:
           name = df_DAX30.loc[df_DAX30['ISIN'] == isin].iloc[0]['Name']

       if isin in df_AEX.ISIN.values:
           name = df_AEX.loc[df_AEX['ISIN'] == isin].iloc[0]['Name']

       elif isin in df_CAC40.ISIN.values:
           name = df_CAC40.loc[df_CAC40['ISIN'] == isin].iloc[0]['Name']

       elif isin in df_IBEX35.ISIN.values:
           name = df_IBEX35.loc[df_IBEX35['ISIN'] == isin].iloc[0]['Name']

       elif isin in df_FTSE100.ISIN.values:
           name = df_FTSE100.loc[df_FTSE100['ISIN'] == isin].iloc[0]['Name']

       elif isin in df_SP1500.ISIN.values:
           name = df_SP1500.loc[df_SP1500['ISIN'] == isin].iloc[0]['Name']

       elif isin in df_NIKKEI300.ISIN.values:
           name = df_NIKKEI300.loc[df_NIKKEI300['ISIN'] == isin].iloc[0]['Name']

       elif isin in df_HSI.ISIN.values:
           name = df_HSI.loc[df_HSI['ISIN'] == isin].iloc[0]['Name']

       elif isin in df_SZSE.ISIN.values:
           name = df_SZSE.loc[df_SZSE['ISIN'] == isin].iloc[0]['Name']

       return name

    return name

def get_optimize_objective_char(portfolio_risk_input):
    return {
        0: 'v',
        1: 's',
        2: 'r'
    }[portfolio_risk_input]

def get_time_interval_char(portfolio_time_period_interval_input):
    return {
        0: 'm',
        1: 'd'
    }[portfolio_time_period_interval_input]

def construct_graph(user):
    #obtain gui_weights (percentage) and get_acp (returns). Then calculate daily (weighted) portfolio return
    procedure = user.req_history[-1][1]
    df_weights = procedure.gui_weights.copy()
    comps = []
    for i, row in procedure.gui_weights.iterrows():
        comps.append(i)
    df_acp = sql_handler.getACP(user.period_start, '2019-11-22', comps)
    df_acp.insert(0, 'date', df_acp.index)
    df_acp.reset_index(inplace = True, drop = True)

    #obtain portfolio return for each date in get_acp since base_date (date where every selected ISIN has a value)
    x_values = []
    y_values = []
    #find base_date_index
    for i, row in df_acp.iloc[1:].iterrows():
        if row.isnull().any():
            continue
        else:
            base_date_index = i
            break

    print('MESSAGE: Portfolio graph is being constructed (1/2)')
    for i, row in df_acp.iloc[1:].iterrows():
        if i == 0 or row.isnull().any():
            continue
        ret_values = []
        #for each date i, get return of each stock (ret_values) relative to base_date
        for col in df_acp.columns[1:]:
            ret = ((df_acp.iloc[i][col] - df_acp.iloc[base_date_index][col]) / df_acp.iloc[base_date_index][col])*100
            ret_values.append(ret)
        ctr = 0
        y = 0
        #for each date i, calculate the weighted portfolio return (y)
        for k in ret_values:
            percent = df_weights.iloc[ctr][0]
            y += k * percent
            ctr += 1
        #append portfolio return (y) to y_values
        y_values.append(y)
        #append date i to x_values
        x_values.append(df_acp.iloc[i][0])

    df_graph = pd.DataFrame({'date': x_values, 'portfolio return': y_values})
    base_date = df_acp.iloc[base_date_index][0].strftime('%d.%m.%Y')
    print('MESSAGE: Portfolio graph is being constructed (2/2)')

    #only plot DAX graph if user.period_start is later than 2005-01-13
    dt_period_start = dt.strptime(user.period_start, '%Y-%m-%d')
    dt_first_DAX_date = dt.strptime('2005-01-13', '%Y-%m-%d')
    if dt_period_start < dt_first_DAX_date:
        return df_graph, base_date
    else:
        #obtain DAX index get_acp (returns)
        df_DAX_acp = sql_handler.getACP(user.period_start, '2019-11-22', ['DE0008469008'])
        df_DAX_acp.insert(0, 'date', df_DAX_acp.index)
        df_DAX_acp.reset_index(inplace = True, drop = True)
        DAX_x_values = []
        DAX_y_values = []

        print('MESSAGE: DAX graph is being constructed (1/2)')
        i_ctr = 1
        for i, row in df_DAX_acp.iloc[1:].iterrows():
            if i == 0 or row.isnull().any():
                continue
            # for each date i, get return of relative to base_date
            y = ((df_DAX_acp.iloc[i][1] - df_DAX_acp.iloc[base_date_index][1]) / df_DAX_acp.iloc[base_date_index][
                    1]) * 100
            # append DAX return (y) to DAX_y_values
            DAX_y_values.append(y)
            # append date i to DAX_x_values
            DAX_x_values.append(df_acp.iloc[i][0])
            i_ctr = i

        df_DAX_graph = pd.DataFrame({'date': DAX_x_values, 'DAX return': DAX_y_values})
        print('MESSAGE: DAX graph is being constructed (2/2)')

        return df_graph, base_date, df_DAX_graph

def construct_figure(base_date, user_period_end, df_graph, df_DAX30_graph):
    # construct scatterplot from df_graph: x_values (date) and y_values (portfolio return)
    x_values = df_graph['date'].tolist()
    y_values = df_graph['portfolio return'].tolist()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x = x_values,
        y = y_values,
        name = 'Portfolio'
    ))

    if df_DAX30_graph is not None:
    # construct scatterplot from df_DAX30_graph: x_values (date) and y_values (DAX30 return)
        DAX30_x_values = df_DAX30_graph['date'].tolist()
        DAX30_y_values = df_DAX30_graph['DAX return'].tolist()
        fig.add_trace(go.Scatter(
            x=DAX30_x_values,
            y=DAX30_y_values,
            name='DAX'
        ))

    fig.update_layout(
        title='Portfolio Return since {} [%]'.format(base_date),
        plot_bgcolor='#ffffff',  # f4f4f4 (light grey)
        paper_bgcolor='#ffffff',  # f4f4f4 (light grey)
        xaxis=dict(showgrid=True, gridwidth=1, gridcolor='#f4f4f4'),
        yaxis=dict(showgrid=True, gridwidth=1, gridcolor='#f4f4f4'),
        margin=dict(t=80),
        shapes=[
            dict(
                type='rect',
                xref='x',
                yref='paper',
                x0=user_period_end,
                y0=0,
                x1='2019-11-22',
                y1=1,
                fillcolor='#fafafa',
                opacity=0.8,
                layer='below',
                line_width=0
            )
        ]
    )

    return fig

def get_portfolio_result(user):
    procedure = user.req_history[-1][1]
    s = 'Sharpe ratio: {:.2f}'.format(procedure.sharpe_ratio)
    r = 'Total return: {:.2f}%'.format(procedure.total_return)
    std = 'Standard dev.: {:.2f}'.format(procedure.total_volatility)

    #modify copy of gui_weights: round results, add share name and ISIN column and rename columns properly
    portfolio_table_output = procedure.gui_weights.copy()
    portfolio_table_output['percent_portfolio'] = portfolio_table_output['percent_portfolio'].apply(lambda x:x*100)
    portfolio_table_output['percent_portfolio'] = portfolio_table_output['percent_portfolio'].apply(lambda x:round(x,2))
    portfolio_table_output['amount_eur'] = portfolio_table_output['amount_eur'].apply(lambda x: round(x, 2))
    names = []
    for i, row in procedure.gui_weights.iterrows():
        name = get_asset_name_to_isin_list(i)
        names.append(name)
    portfolio_table_output['Name'] = names
    portfolio_table_output['ISIN'] = portfolio_table_output.index
    portfolio_table_output = portfolio_table_output[['Name', 'ISIN', 'percent_portfolio', 'amount_eur']]
    portfolio_table_output.columns = ['Name', 'ISIN', 'Weight [%]', 'Amount [EUR]']
    #portfolio_table_output.append({'Name': [None], 'ISIN': [None], 'Amount [EUR]': - last (sum) row tbd

    #construct scatterplot with historic portfolio return
    construct_graph_result = construct_graph(user)
    df_graph = construct_graph_result[0]
    base_date_graph = construct_graph_result[1]
    user_period_end = user.req_history[-1][0].period_end #for highlighting grey plot area (period end - now)
    if len(construct_graph_result) > 2: #DAX graph has been added
        df_DAX_graph = construct_graph_result[2]
        figure = construct_figure(base_date_graph, user_period_end, df_graph, df_DAX_graph)
    else:
        figure = construct_figure(base_date_graph, user_period_end, df_graph, None)

    #construct table with weights
    data = portfolio_table_output.to_dict('records')
    columns = [{'name': i, 'id': i} for i in portfolio_table_output.columns]

    return user.id, s, r, std, data, columns, df_graph, figure

### Execute program
if __name__ == '__main__':
   app.run_server(debug=True)