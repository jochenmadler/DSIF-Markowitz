
import User as us
import pandas as pd
from datetime import datetime
start=datetime.now()

data = pd.DataFrame(data=[[3,2,3],[3,2,3],[3,2,3],[1,2,3]],columns=[1,2,3],index=["2018-01-01","2018-01-02","2018-01-03","2018-02-02"])
data.index = pd.to_datetime(data.index)
data = data.resample('1M').max()

user = us.User("testID", 10000,['de000a1ewww0', 'de0008404005', 'de000basf111','de000a1ewww4'], optimize_objective="s", broker_fix=0)
user.optimize_req()
print("done optimizing")
user.rebalance_req()
print("done rebalancing")

print (datetime.now()-start)
