# Version: 3.0

# Workflow:
# 1. OptimizeProcedure gets initialized with optimize_request(either optimizeRequest or optimizeRebalance)
# 2. OptimizeProcedure obtains data and creates optimizeData
# 3. OptimizeProcedure initializes optimizeResult

from abc import ABC, abstractmethod
import scipy.optimize as sco
import numpy as np
import SQLHandler as sh
import ObjectiveFunction as of
import pandas as pd
import User as u
import sys

class optimizeData:
    data = None
    ISIN_list = None
    period_list = None
    #current_prices = None
    return_df = None

    def __init__(self, data, time_interval):

        #ToDO:implement conversion to monthly data (test)
        if time_interval == 'm':
            data.index = pd.to_datetime(data.index)
            data_res = data.resample('1M').max()
            data = data_res

        #ToDo:implement handling von NAs in data (zurückgestellt)
        #if data.isnull().values.any():
        #    assert("")

        # UNCOMMENT FOR TESTING
        #----------------------------------------------------------------------------
        #data =  pd.read_excel("AUS_testData.xlsx", sheet_name = "Tabelle1")
        #----------------------------------------------------------------------------

        self.data = data
        self.ISIN_list = data.columns
        self.period_list = data.index
        self.current_prices = data.iloc[len(self.period_list) - 1,]

        # convert adjPrice into returns in return_df
        return_df = pd.DataFrame(index=self.period_list[1:], columns=self.ISIN_list, dtype=float)
        for ct in range(1, len(self.period_list)):
            for ct2 in range(0, len(self.ISIN_list)):
                return_df.iloc[ct - 1, ct2] = (self.data.iloc[ct, ct2] / self.data.iloc[ct - 1, ct2]) - 1
        self.return_df = return_df


class optimizeResult:
    #ToDo: check if need to be converted to spefic time period (example p.a.)
    sharpe_ratio = -10000
    total_volatility = 100000
    total_return = -10000

    transaction_cost = 0
    security_weights = None
    current_capital = None
    dev_graph = None
    gui_weights = None

class optimizeProcedure():
    optimize_request = None
    optimize_data = None
    optimize_result = None
    obj_function = None

    def __init__(self, optimize_request):

        self.optimize_request = optimize_request

        raw_data = sh.getACP(optimize_request.user.period_start, optimize_request.period_end, optimize_request.user.ISIN_list)
        self.optimize_data = optimizeData(raw_data, optimize_request.user.time_interval)

        # add different objFunctions here
        self.obj_function = of.objFunction_basicTrans()

        self.optimize_result = optimizeResult()


    def optimize(self):

        # initial request with equal start weights and transaction cost occurring for each purchase
        if (isinstance(self.optimize_request, u.optimizeRequest)):
            initial_weights = len(self.optimize_data.ISIN_list) * [1 / (len(self.optimize_data.ISIN_list)), ]
            zerocost_weights = len(self.optimize_data.ISIN_list) * [0, ]

        # rebalance request with start weights from last procedure and cost ocurring for each rebalancing
        else:
            initial_weights = self.optimize_request.user.req_history[-1][1].security_weights.values[0]
            zerocost_weights = initial_weights

        # constraint: all money gets invested
        cons = {'type': 'eq', 'fun': lambda x: -(np.sum(x) - 1)}

        # bounds: no short positions
        bounds = tuple((0, 1) for x in range(len(self.optimize_data.ISIN_list)))

        # using minimize as sco does not offer maximize method
        opt_portfolio = sco.minimize(

            # minimize: negative objFunction
            fun = self.obj_function.function,

            x0= initial_weights,

            args = (self, zerocost_weights),

            method='SLSQP',

            bounds=bounds,

            constraints=cons,

        )

        # update current budget after optimizing
        self.generate_guioutput()
        self.optimize_request.user.budget = self.optimize_request.user.budget * (self.optimize_result.total_return/100 + 1)
        self.optimize_result.current_capital = self.optimize_request.user.budget

    def generate_guioutput(self):
        print('')
        gui_weights = pd.DataFrame(columns=['percent_portfolio', 'amount_eur'], index = self.optimize_data.ISIN_list)
        test = self.optimize_result.security_weights.values
        gui_weights["percent_portfolio"] = self.optimize_result.security_weights.values[0]
        gui_weights["amount_eur"] = self.optimize_result.security_weights.values[0]
        gui_weights.loc[:, 'amount_eur'] *= self.optimize_request.user.budget
        self.optimize_result.gui_weights = gui_weights

        # ToDo: Implement the construction of the dev_graph


