import scipy.optimize as sco
import numpy as np
import SQLHandler as sh
import ObjectiveFunction as of


#provided by GUI user-input
class optimizeRequest:
    budget = None
    ISIN_list = None
    time_interval = None
    period_start = None
    broker_fix = None
    broker_var = None
    split_shares = None
    optimize_objective = None

    def __init__(self, budget, ISIN_list, optimize_objective = "s", time_interval = 'd' ,period_start = '2019-01-01',broker_fix = 0,broker_var = 0,split_shares = True):
        self.budget = budget
        self.ISIN_list = ISIN_list
        self.optimize_objective = optimize_objective
        self.time_interval = time_interval
        self.period_start = period_start
        self.broker_fix = broker_fix
        self.broker_var = broker_var
        self.split_shares = split_shares

#generated from DataBase based on request parameters
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

#generated based on Data and objective function
class optimizeResult:
    sharpe_ratio = -10000
    total_volatility = None
    total_return = None
    transaction_cost = 0
    security_weights = None
    dev_graph = None

#comman center
class optimizeProcedure:
    optimize_request = None
    optimize_data = None
    optimize_result = None
    obj_function = None

    def __init__(self, optimize_request):
        self.optimize_request = optimize_request

        #generate optimize_data
        self.optimize_data = optimizeData(sh.getACP(optimize_request.period_start, '2019-01-11', optimize_request.ISIN_list))

        #ToDo: Decide for which KPI to optimize for
        #define objective function to use
        if((self.optimize_request.broker_fix == 0) & (self.optimize_request.broker_fix == 0)):
            self.obj_function = of.objFunction_noTrans()
        else:
            self.obj_function = of.objFunction_basicTrans()

        self.optimize_result = optimizeResult()

        self.optimize()

    #ToDo: check if there exists an implementation for whole shares
    def wholeShareConstraint(self, x):
        rest = 0
        for ct in range(0, len(x)):
            price = self.optimize_data.current_prices.iloc[ct]
            rest = rest + abs((x[ct] * self.optimize_request.budget) % price)
        return rest


    def optimize(self):

        #ToDo: check if there exists an implementation for whole shares
        if self.optimize_request.split_shares == False:
            cons = ({'type': 'ineq', 'fun': lambda x: -(np.sum(x) - 1)},
                    {'type': 'eq', 'fun': self.wholeShareConstraint})
        else:
            cons = {'type': 'ineq', 'fun': lambda x: -(np.sum(x) - 1)}

        # Bounds: no short positions
        bounds = tuple((0, 1) for x in range(len(self.optimize_data.ISIN_list)))

        # using minimize as sco does not offer maximize method
        opt_portfolio = sco.minimize(

            # minimize: negative objFunction
            fun = self.obj_function.function,

            # initial solution: equal weights
            x0=len(self.optimize_data.ISIN_list) * [1 / (len(self.optimize_data.ISIN_list)), ],

            #
            args = self,


            method='SLSQP',
            bounds=bounds,
            constraints=cons,

            #TODO: check further solving methods


        )



