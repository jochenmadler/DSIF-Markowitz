import scipy.optimize as sco
import numpy as np
import pandas as pd
from numpy.core._multiarray_umath import ndarray
import Broker as bk

class resultPortfolio:
    transaction_cost = 0
    return_df = None
    sharpe_ratio = - 100000
    total_volatility = None
    security_weights = None
    obj_function_used = None
    port_return = None

class dataSource:
    #data contains the adjusted prices for all securities
    data = None
    no_securities = None
    no_timePeriods = None
    columns = None
    time_periods = None


    def __init__(self, data):
        self.data = data
        self.columns = data.columns
        self.time_periods = data.index
        self.no_securities = len(self.columns)
        self.no_timePeriods = len(self.time_periods)

class optimizeInput:
    data_source = None
    result_portfolio = resultPortfolio()
    budget = None
    broker = None

    def __init__(self, dataSource):
        self.data_source = dataSource

class optimizeProcedure:
    broker = None
    budget = None
    optimize_input = None
    obj_Function = None

    def __init__(self,objFunction, optimizeInput, broker = bk.testBroker(), budget = 10000):
        self.obj_Function = objFunction
        self.optimize_input = optimizeInput
        self.budget = budget
        optimizeInput.budget = budget
        self.broker = broker
        optimizeInput.broker = broker


    def optimize(self):

        # Constraint: sum of all weights should be equal to 1
        cons = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})

        # Bounds: no short positions
        bounds = tuple((0, 1) for x in range(self.optimize_input.data_source.no_securities))

        # using minimize as sco does not offer maximize method
        opt_portfolio = sco.minimize(

            # minimize: negative objFunction
            fun = self.obj_Function.function,

            #
            args = self.optimize_input,

            # initial solution: equal weights
            x0 = self.optimize_input.data_source.no_securities * [1 / self.optimize_input.data_source.no_securities, ],


            bounds=bounds,
            constraints=cons,
            #TODO: check further solving methods
            method = 'SLSQP',

        )

        #print("optimization result: sharpeRatio of " + str(self.result_portfolio.sharpe_ratio))



