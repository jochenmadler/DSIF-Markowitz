# Version: 2.0

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

class optimizeData:
    data = None
    ISIN_list = None
    period_list = None
    current_prices = None

    def __init__(self, data, time_interval = 'd'):

        #ToDO:implement conversion to monthly data
        if time_interval == 'm':
            pass

        #data sanity check for NAs
        #ToDo:implement handling von NAs in data
        if data.isnull().values.any():
            pass

        self.data = data
        self.ISIN_list = data.columns
        self.period_list = data.index
        self.current_prices = data.iloc[len(self.period_list) -1, ]

class optimizeResult:
    sharpe_ratio = -10000
    total_volatility = 100000
    total_return = -10000
    transaction_cost = 0
    security_weights = None
    dev_graph = None
    gui_weights = None

class optimizeProcedure():
    optimize_request = None
    optimize_data = None
    optimize_result = None
    obj_function = None

    def __init__(self, optimize_request):

        self.optimize_request = optimize_request

        #ToDo: delete quick fix for testing
        #generate optimize_data

        raw_data = sh.getACP(optimize_request.user.period_start, optimize_request.period_end, optimize_request.user.ISIN_list)
        self.optimize_data = optimizeData(raw_data)

        #-------------------------------------------------------------------------------------------------------------
        #data = [[3,4,2,3],[5,2,3,4],[2,4,2,4],[3,5,2,7],[4,2,5,3],[2,6,2,3]]
        #df = pd.DataFrame(columns=['de000a1ewww0', 'de0008404005', 'de000basf111','de000a1ewww4'],index=["T1","T2","T3","T4","T5","T6"],data=data)
        #self.optimize_data = optimizeData(df)
        #-------------------------------------------------------------------------------------------------------------

        self.obj_function = of.objFunction_basicTrans()

        #create empty optimizeResult obj in which result will be stored
        self.optimize_result = optimizeResult()


    def optimize(self):

        if (isinstance(self.optimize_request, u.optimizeRequest)):
            initial_weights = len(self.optimize_data.ISIN_list) * [1 / (len(self.optimize_data.ISIN_list)), ]
            zerocost_weights = len(self.optimize_data.ISIN_list) * [0, ]
        else:
            initial_weights = self.optimize_request.user.req_history[-1][1].security_weights.values[0]
            zerocost_weights = initial_weights

        cons = {'type': 'eq', 'fun': lambda x: -(np.sum(x) - 1)}

        # Bounds: no short positions
        bounds = tuple((0, 1) for x in range(len(self.optimize_data.ISIN_list)))

        # using minimize as sco does not offer maximize method
        opt_portfolio = sco.minimize(

            # minimize: negative objFunction
            fun = self.obj_function.function,

            # initial solution: equal weights
            x0= initial_weights,

            args = (self, zerocost_weights),

            # TODO: check further solving methods
            method='SLSQP',

            bounds=bounds,

            constraints=cons,


        )



    def generate_guioutput(self):
        gui_weights = pd.DataFrame(columns=['percent_portfolio', 'amount_eur'], index = self.optimize_data.ISIN_list)
        test = self.optimize_result.security_weights.values
        gui_weights["percent_portfolio"] = self.optimize_result.security_weights.values[0]
        gui_weights["amount_eur"] = self.optimize_result.security_weights.values[0]
        gui_weights.loc[:, 'amount_eur'] *= self.optimize_request.user.budget
        self.optimize_result.gui_weights = gui_weights

        dev_graph = pd.DataFrame(columns=['date', 'return', 'return acc'], index=self.optimize_data.period_list)


