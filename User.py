# Version: 3.1

# Workflow
# 1. User gets initialized with User(id, budget, ISIN_list, etc. )
#   1.1 Specifications of request are saved in user to be easily accessible for all optimizationProcedures
# 2. User requests initial optimization with userObj.optimize_req(period_end)
#   2.1 Tuple(Request, Result) gets appended to userObj.req_history
# 3. User requests portfolio rebalancing with userObj.rebalance_req(period_end)
#   3.1 Previous weights are obtained from last element of userObj.req_history
#   3.2 Optimization configuration is obtained from user
#   3.3 Tuple(Request, Result) gets appended to userObj.req_history

import datetime
import OptimizeProcedure as op
import SQLHandler as sh

class User():
    id = None
    broker_fix = None
    broker_var = None
    #split_shares = None
    optimize_objective = None
    initial_budget = None
    budget = None
    ISIN_list = None
    time_interval = None
    period_start = None
    req_history = []
    portfolio_history = None

    def __init__(self, id, budget, ISIN_list,
                 time_interval = 'd' ,optimize_objective = "s", period_start = '2018-01-01', broker_fix = 0.1,
                 broker_var = 0, split_shares = True):

        self.id = id
        self.budget = budget
        self.initial_budget = budget

        sorted_ISIN_list = (sh.getACP('2019-01-01', '2019-01-01', ISIN_list)).columns #2019-02-01 davor
        self.ISIN_list = sorted_ISIN_list

        self.time_interval = time_interval
        self.optimize_objective = optimize_objective
        self.period_start = period_start
        self.broker_fix = broker_fix
        self.broker_var = broker_var
        self.split_shares = split_shares


    def optimize_req(self, period_end = '2018-10-01'):
        optimize_request = optimizeRequest()
        optimize_request.user = self
        optimizeRequest.period_end = period_end
        optimize_request.id = str(self.id) + "_opt_" + str(datetime.datetime.now())
        optimize_procedure = op.optimizeProcedure(optimize_request)
        optimize_procedure.optimize()
        self.req_history.append([optimize_request,optimize_procedure.optimize_result])



    def rebalance_req(self, period_end = '2019-10-01'):

        period_start = self.req_history[-1][0].period_end
        weigthts = self.req_history[-1][1].security_weights
        prices = sh.getACP(period_start, period_end, self.ISIN_list)

        first_row = prices.iloc[0,]
        last_row = prices.iloc[-1,]
        ret_total = sum(((last_row - first_row) / first_row) * weigthts.iloc[0,])
        self.budget = self.budget * (ret_total + 1)


        optimize_rebalance = optimizeRebalance()
        optimize_rebalance.user = self
        optimize_rebalance.period_end = period_end
        optimize_rebalance.id = str(self.id) + "_reb_" + str(datetime.datetime.now())
        optimize_procedure = op.optimizeProcedure(optimize_rebalance)
        optimize_procedure.optimize_result = op.optimizeResult()


        optimize_procedure.optimize()
        self.req_history.append([optimize_rebalance, optimize_procedure.optimize_result])


class optimizeRequest:
    user = None
    id = None
    period_end = None


class optimizeRebalance:
    user = None
    id = None
    period_end = None
