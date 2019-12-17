
import OptimizeProcedure as op
import SQLHandler as sh

import time
start_time = time.time()

comps = ['adidas', 'allianz','basf','bmw','bayer']
data=sh.getAP('2019-01-01', '2019-01-11', comps)

#data = [[3,4,2,3],[5,2,3,4],[2,4,2,4],[3,5,2,7],[4,2,5,3],[2,6,2,3]]
#df = pd.DataFrame(columns=["A","B","C","D"],index=["T1","T2","T3","T4","T5","T6"],data=data)


gui_request = op.optimizeRequest(10000, comps)
procedure = op.optimizeProcedure(optimize_request=gui_request)
print("done")
