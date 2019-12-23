# Version 1.0.0
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from datetime import datetime as dt

# import function to call data from Alex' SQLHandler
from SQLHandler import findComp
# import function to optimize portfolio from Marcl's OptimizeProcedure
import OptimizeProcedure as op

# preload all stock data (from local PostgreSQL) into df's: [0: Name, 1: ISIN, 2: Index]
df_DAX30 = findComp('DAX30', 'Index', ['Name', 'ISIN', 'Index'], 'companies')
df_DAX30.columns = ['Name', 'ISIN', 'Index']
df_CAC40 = findComp('CAC40', 'Index', ['Name', 'ISIN', 'Index'], 'companies')
df_CAC40.columns = ['Name', 'ISIN', 'Index']
df_FTSE100 = findComp('FTSE100', 'Index', ['Name', 'ISIN', 'Index'], 'companies')
df_FTSE100.columns = ['Name', 'ISIN', 'Index']
df_HSI = findComp('HangSengIndex', 'Index', ['Name', 'ISIN', 'Index'], 'companies')
df_HSI.columns = ['Name', 'ISIN', 'Index']
df_IBEX35 = findComp('IBEX35', 'Index', ['Name', 'ISIN', 'Index'], 'companies')
df_IBEX35.columns = ['Name', 'ISIN', 'Index']
df_SSE = findComp('SSE', 'Index', ['Name', 'ISIN', 'Index'], 'companies')
df_SSE.columns = ['Name', 'ISIN', 'Index']

# set up options for asset mix - cut df's and create dictionary for all options
# make DAX30 df to dict: d_DAX30
df_ = df_DAX30.drop(df_DAX30.columns[[1,2]], axis=1)
df_.rename(columns={'Name': 'DAX30'}, inplace=True)
d_Dax30 = df_.to_dict('list')

# make CAC40 df to dict: d_CAC40
df_ = df_CAC40.drop(df_CAC40.columns[[1,2]], axis=1)
df_.rename(columns={'Name': 'CAC40'}, inplace=True)
d_CAC40 = df_.to_dict('list')

# make FTSE100 df to dict: d_FTSE100
df_ = df_FTSE100.drop(df_FTSE100.columns[[1,2]], axis=1)
df_.rename(columns={'Name': 'FTSE100'}, inplace=True)
d_FTSE100 = df_.to_dict('list')

# make HSI df to dict: d_HSI
df_ = df_HSI.drop(df_HSI.columns[[1,2]], axis=1)
df_.rename(columns={'Name': 'HSI'}, inplace=True)
d_HSI = df_.to_dict('list')

# make IBEX35 df to dict: d_IBEX35
df_ = df_IBEX35.drop(df_IBEX35.columns[[1,2]], axis=1)
df_.rename(columns={'Name': 'IBEX35'}, inplace=True)
d_IBEX35 = df_.to_dict('list')

# make SSE df to dict: d_SSE
df_ = df_SSE.drop(df_SSE.columns[[1,2]], axis=1)
df_.rename(columns={'Name': 'SSE'}, inplace=True)
d_SSE = df_.to_dict('list')

# concatenate all dicts to one: all_stock_options
all_stock_options = dict(d_Dax30, **d_CAC40, **d_FTSE100, **d_HSI, **d_IBEX35, **d_SSE)
print(all_stock_options)

# set up app and design style
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# server = app.server - may be implemented at a later stage


# set up app layout (the actual GUI displayed)
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
                **Portfolio Name:**
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
                          placeholder='my world portfolio',
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
                          placeholder='1000',
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
                **Risk profile:**
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
                           0: 'averse',
                           1: 'neutral',
                           2: 'affine'
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
                    dcc.Checklist(id='portfolio_asset_SSE_activate',
                                  options=[{'label': 'SSE', 'value': 'SSE'}])
                ], style={
                    'width': '30%',
                    'float': 'left',
                    'display': 'table-cell',
                    'verticalAlign': 'middle',
                    'horizontalAlign': 'middle'
                }),
                html.Div([
                    dcc.Dropdown(id='portfolio_asset_SSE_input',
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

        ##INPUT 6: 'portfolio_asset_split_input'
        html.Div([
            html.Div([
                dcc.Markdown('''
                    **Split shares:**
                    ''')
            ], style={
               'width': '50%',
               'float': 'left',
               'display': 'table-cell',
               'verticalAlign': 'middle'
           }),
           html.Div([
               dcc.Slider(id='portfolio_asset_split_input',
                          min=0,
                          max=1,
                          marks={
                              0: 'No',
                              1: 'Yes',
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
            'verticalAlign': 'middle'
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

            #first row: start date
            html.Div([
                html.Div([
                    #left
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
                    dcc.DatePickerSingle(
                        id='portfolio_time_period_start_input',
                        date=dt(1990, 1, 1),
                        min_date_allowed=dt(1990, 1, 1),
                        max_date_allowed=dt(2019, 9, 1),
                        display_format='DD/MM/YYYY'
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

            #second row: end date
            html.Div([
html.Div([
                    #left
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
                    dcc.DatePickerSingle(
                        id='portfolio_time_period_end_input',
                        date=dt(2018, 9, 1),
                        min_date_allowed=dt(1991, 1, 1),
                        max_date_allowed=dt(2019, 9, 1),
                        display_format='DD/MM/YYYY'
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

        html.Hr(style={
            'width': '99%',
            'display': 'inline-block'
        }),

        ##INPUT 8: 'portfolio_creation_input'
        html.Div([
            html.Button(id='portfolio_creation_input',
                        children='Create Portfolio')
        ], style={
            'verticalAlign': 'middle'
        })


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
            html.H5(
                id='portfolio_name_output',
                children='My world portfolio',
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

        ##OUTPUT 2: 'portfolio_pie_chart_output'
        html.Div([
            dcc.Graph(id='portfolio_pie_chart_output')
        ]),

        html.Hr(style={
            'width': '99%',
            'display': 'inline-block'
        }),

        ##OUTPUT 3: 'portfolio_table_output'
        html.Div([
            dcc.Graph(id='portfolio_table_output')
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
#1: 'portfolio_name_input'
#2: 'portfolio_amount_input'
#3: 'portfolio_risk_input'
#4.1.1: 'portfolio_asset_DAX30_activate'
#4.1.2: 'portfolio_asset_DAX30_input'
#4.2.1: 'portfolio_asset_CAC40_activate'
#4.2.2: 'portfolio_asset_CAC40_input'
#4.3.1: 'portfolio_asset_FTSE100_activate'
#4.3.2: 'portfolio_asset_FTSE100_input'
#4.4.1: 'portfolio_asset_IBEX35_activate'
#4.4.2: 'portfolio_asset_IBEX35_input'
#4.5.1: 'portfolio_asset_HSI_activate'
#4.5.2: 'portfolio_asset_HSI_input'
#4.6.1: 'portfolio_asset_SSE_activate'
#4.6.2: 'portfolio_asset_SSE_input'
#5: 'portfolio_creation_input'

#OUTPUTS:
#1: 'portfolio_name_output'
#2: 'portfolio_pie_chart_output'
#3: 'portfolio_table_output'

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

# activate CAC40 Dropdown menu when CAC40 Checklist is ticked
@app.callback(Output('portfolio_asset_CAC40_input', 'options'),
              [Input('portfolio_asset_CAC40_activate', 'value')])
def set_CAC40_Dropdown(value_CAC40):
    if value_CAC40 is not None and value_CAC40:
        return [{'label': i, 'value': i} for i in all_stock_options[value_CAC40[0]]]
    else:
        return [{'label': '', 'value': ''}]
# select all options in CAC_40 when CAC40 Checklist is ticked - #TODO

# activate FTSE100 Dropdown menu when FTSE100 Checklist is ticked
@app.callback(Output('portfolio_asset_FTSE100_input', 'options'),
              [Input('portfolio_asset_FTSE100_activate', 'value')])
def set_FTSE100_Dropdown(value_FTSE100):
    if value_FTSE100 is not None and value_FTSE100:
        return [{'label': i, 'value': i} for i in all_stock_options[value_FTSE100[0]]]
    else:
        return [{'label': '', 'value': ''}]
# select all options in FTSE_100 when FTSE100 Checklist is ticked - #TODO


# activate IBEX35 Dropdown menu when IBEX35 Checklist is ticked
@app.callback(Output('portfolio_asset_IBEX35_input', 'options'),
              [Input('portfolio_asset_IBEX35_activate', 'value')])
def set_IBEX35_Dropdown(value_IBEX35):
    if value_IBEX35 is not None and value_IBEX35:
        return [{'label': i, 'value': i} for i in all_stock_options[value_IBEX35[0]]]
    else:
        return [{'label': '', 'value': ''}]
# select all options in IBEX_35 when IBEX35 Checklist is ticked - #TODO

# activate HSI Dropdown menu when HSI Checklist is ticked
@app.callback(Output('portfolio_asset_HSI_input', 'options'),
              [Input('portfolio_asset_HSI_activate', 'value')])
def set_HSI_Dropdown(value_HSI):
    if value_HSI is not None and value_HSI:
        return [{'label': i, 'value': i} for i in all_stock_options[value_HSI[0]]]
    else:
        return [{'label': '', 'value': ''}]
# select all options in HSI when HSI Checklist is ticked - #TODO

# activate SSE Dropdown menu when SSE Checklist is ticked
@app.callback(Output('portfolio_asset_SSE_input', 'options'),
              [Input('portfolio_asset_SSE_activate', 'value')])
def set_SSE_Dropdown(value_SSE):
    if value_SSE is not None and value_SSE:
        return [{'label': i, 'value': i} for i in all_stock_options[value_SSE[0]]]
    else:
        return [{'label': '', 'value': ''}]
# select all options in SSE when SSE Checklist is ticked - #TODO


@app.callback(Output('portfolio_name_output', 'children'), #2 OUTPUT graphs can be added here
              [Input('portfolio_creation_input', 'n_clicks')],
              [State('portfolio_name_input', 'value')])

###DEF 1: UPDATE PORTFOLIO NAME
def update_portfolio_name(n_clicks, portfolio_name_input):
    return '''{}'''.format(portfolio_name_input)


# test request (create)
request = op.optimizeRequest(1000,['de000a1ewww0', 'de0008404005', 'de000basf111'])
procedure = op.optimizeProcedure(request)
s = procedure.optimize_result.sharpe_ratio


print('DONE')

# execute program

if __name__ == '__main__':
    app.run_server(debug=True)