
import User as us

from datetime import datetime
start=datetime.now()


user = us.User("testID", 123, 10000,['de000a1ewww0', 'de0008404005', 'de000basf111','de000a1ewww4'], optimize_objective="r")
user.optimize_req()
print("done optimizing")
user.rebalance_req()
print("done rebalancing")

print (datetime.now()-start)
