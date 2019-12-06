from abc import ABC, abstractmethod
import scipy.optimize as sco
import numpy as np
import pandas as pd
import OptimizeProcedure as op
import ObjectiveFunction as of



data = [[3,4,2,3],[5,2,3,4],[2,4,2,4],[3,5,2,7],[4,2,5,3],[2,6,2,3]]
df = pd.DataFrame(columns=["A","B","C","D"],index=["T1","T2","T3","T4","T5","T6"],data=data)

ds = op.dataSource(df)
op = op.optimizeProcedure(of.objFunction_basicTrans,op.optimizeInput(ds))
op.optimize()
print("done")