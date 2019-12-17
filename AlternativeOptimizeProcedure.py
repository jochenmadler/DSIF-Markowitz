

#model with basic transaction cost
class objFunction_basicTrans(objFunction):
    name = "objFunction_basicTransactionCost"


    def function(weights, optimizeInput):

        variable_cost = optimizeInput.broker.variable_cost
        fixed_cost = optimizeInput.broker.fixed_cost

        dataSource = optimizeInput.data_source

        # convert adjPrice into Returns
        return_df = pd.DataFrame(index=dataSource.time_periods[1:], columns=dataSource.columns, dtype=float)

        for ct in range(1, dataSource.no_timePeriods):
            for ct2 in range(0, dataSource.no_securities):
                return_df.iloc[ct - 1, ct2] = (dataSource.data.iloc[ct, ct2] / dataSource.data.iloc[ct - 1, ct2]) - 1

        port_weights: ndarray = np.array(weights)

        # get the covariance matrix
        cov_Mat = return_df.cov()

        # get the total variance -> sum(covariance(A-B) * weight A * weight B)
        total_cov = np.dot(np.dot(cov_Mat, port_weights), port_weights.T)

        # convert variance into stddev
        port_vol = np.sqrt(total_cov)

        # calculate return mean for each column
        avg_returns = return_df[dataSource.columns].mean()

        # calculate total portfolio return based on weights
        port_return = np.sum(avg_returns * port_weights)

        absolute_return = port_return * optimizeInput.budget

        #fixed cost
        amount_securities_to_purchase = 0
        for weight in weights:
            if weight > 0:
                amount_securities_to_purchase = amount_securities_to_purchase + 1
        total_fixed_cost = amount_securities_to_purchase * fixed_cost

        #variable cost
        total_variable_cost = optimizeInput.budget * variable_cost

        total_transaction_cost = total_fixed_cost + total_variable_cost
        absolute_return = absolute_return - total_transaction_cost

        port_return = absolute_return / optimizeInput.budget

        # calculate sharpe ratio
        port_shr = port_return / port_vol

        # save results in resultPortfolio, otherwise the would get lost
        if port_shr > optimizeInput.result_portfolio.sharpe_ratio:
            optimizeInput.result_portfolio.transaction_cost = total_transaction_cost
            objFunction.save(optimizeInput, objFunction_noTrans.name, return_df, port_shr, port_return, port_vol, port_weights)

        return - port_shr

