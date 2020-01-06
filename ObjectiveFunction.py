# Version: 2.0
# objective functions for fixed transaction costs implemented

from abc import ABC, abstractmethod
import numpy as np
import pandas as pd

#skeleton for further implementations of objectiveFunctions
class objFunction(ABC):
    @abstractmethod
    def function(self, dataSource):
        pass

    def save(optimizeProcedure, return_df, port_shr,port_return , port_vol, port_weights):
        optimizeProcedure.optimize_result.sharpe_ratio = port_shr
        optimizeProcedure.optimize_result.total_volatility = port_vol
        optimizeProcedure.optimize_result.security_weights = pd.DataFrame(data=[port_weights.tolist()],
                                                                   columns=optimizeProcedure.optimize_data.ISIN_list, index=["weigths"])
        optimizeProcedure.optimize_result.return_df = return_df
        optimizeProcedure.optimize_result.total_return = port_return


#model with basic transaction cost
class objFunction_basicTrans(objFunction):
    name = "objFunction_basicTransactionCost"

    def function(self, weights, optimizeProcedure, zerocost_weights):

        #ToDo: delete
        print(weights)

        variable_cost = optimizeProcedure.optimize_request.user.broker_var
        fixed_cost = optimizeProcedure.optimize_request.user.broker_fix

        dataSource = optimizeProcedure.optimize_data

        # convert adjPrice into returns ind return_df
        return_df = pd.DataFrame(index=dataSource.period_list[1:], columns=dataSource.ISIN_list, dtype=float)

        for ct in range(1, len(optimizeProcedure.optimize_data.period_list)):
            for ct2 in range(0, len(optimizeProcedure.optimize_data.ISIN_list)):
                return_df.iloc[ct - 1, ct2] = (dataSource.data.iloc[ct, ct2] / dataSource.data.iloc[ct - 1, ct2]) - 1

        port_weights = np.array(weights)

        #get the covariance matrix
        cov_Mat = return_df.cov()

        #get the total variance -> sum(covariance(A-B) * weight A * weight B)
        total_cov = np.dot(np.dot(cov_Mat, port_weights), port_weights.T)

        #convert variance into stddev
        port_vol = np.sqrt(total_cov)

        #calculate return mean for each column
        avg_returns = return_df[dataSource.ISIN_list].mean()

        #calculate total portfolio return based on weights
        port_return = np.sum(avg_returns * port_weights)

        absolute_return = port_return * optimizeProcedure.optimize_request.user.budget

        #include fixed cost
        amount_securities_to_purchase = 0

        for ct in range(0,len(weights)):
            if weights[ct] != zerocost_weights[ct]:
                amount_securities_to_purchase = amount_securities_to_purchase + 1
        total_fixed_cost = amount_securities_to_purchase * fixed_cost

        #include variable cost
        total_variable_cost = optimizeProcedure.optimize_request.user.budget * variable_cost

        total_transaction_cost = total_fixed_cost + total_variable_cost
        absolute_return = absolute_return - total_transaction_cost

        #calculate % return including transaction cost
        port_return = absolute_return / optimizeProcedure.optimize_request.user.budget

        #calculate sharpe ratio
        port_shr = port_return / port_vol

        #save results in resultPortfolio, otherwise they would get lost
        if optimizeProcedure.optimize_request.user.optimize_objective == "s":
            if port_shr > optimizeProcedure.optimize_result.sharpe_ratio:
                objFunction.save(optimizeProcedure, return_df, port_shr, port_return, port_vol, port_weights)
            return - port_shr
        elif optimizeProcedure.optimize_request.user.optimize_objective == "v":
            if port_vol < optimizeProcedure.optimize_result.total_volatility:
                objFunction.save(optimizeProcedure, return_df, port_shr, port_return, port_vol, port_weights)
            return port_vol
        elif optimizeProcedure.optimize_request.user.optimize_objective == "r":
            if port_return > optimizeProcedure.optimize_result.total_return:
                objFunction.save(optimizeProcedure, return_df, port_shr, port_return, port_vol, port_weights)
            return - port_return