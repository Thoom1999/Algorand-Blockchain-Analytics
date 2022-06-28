from sklearn.cluster import affinity_propagation
from utils import *
import time

############## Block Informations ###################
# print(getBlockInfos("8729485"))


############## Tx associated to an asset ###################

# result = dict()
# listTx = []
# for i in range(8729485, 8729500): 
#     data = getTxAssociatedToAnAsset(str(i), "27165954")
#     if data != None: #TODO: remove block where the asset is not traded
#         listTx.append(data)
# result["27165954"] = listTx
# print(result)


############## Detection of asset creation ###################



############## some tests ###################

#print(getJSON(base_URL + "/v2/blocks/" + str(99999999999999)))
#print(getBlockInfos(133574))
#print(getCreatedAssetByBlock(18951072))
#prettyPrint(createdTokenByAddress("CHVKOQ4HM3SCVEAJNNDKMYLPC2VDPGGGXJ4EBYCVPVPHC7O7UDEZBRDYF4"))
"""
for block_n in range(18951072+100, 18951072+150):
    prettyPrint(getTxAssociatedToAsset(block_n, 576840807))
"""
# prettyPrint(getAssetTxInRange(start_block=18951072+100, end_block=18951072+250, asset_id=576840807))

# print(createChunk(10, 103, 13))

# print(createChunk(1, 100, 10))

# def stuff(): 
#     print("coucou")
#     time.sleep(2)

# threads = createAndExecuteThreads(4, stuff)

# calculateProfit("2RY5TUXY25ZVSUFY3KY343MOFBGSFIXI6BLXOWRKQL23EHBZ767DXWSCYM", 784239188, 19179844)
# print(getPoolAddr(685787385))
# print(addLiquidityForFirstTime("6SYDVR4UJQCL5XHCX4JSB7RBG4IH4MEDROU4GKXECEEPBX7VUIZVOY5DSI", 712191147))
# print(calculateProfit("6SYDVR4UJQCL5XHCX4JSB7RBG4IH4MEDROU4GKXECEEPBX7VUIZVOY5DSI", 20568720))
# addLiquidityForFirstTime("SPBOXAGTNY7DEMZRG3VHMJMQL3HGPLEHPAA6VTK5UME5M7FLATXVZGAM7Q", 678773787)
# print(calculateProfit("SPBOXAGTNY7DEMZRG3VHMJMQL3HGPLEHPAA6VTK5UME5M7FLATXVZGAM7Q", 20050776))

print(calculateProfit("AGW3XPUUQP7NDXDSMT33QMMSC6QNJSIXVAWOH4PZYL2ZJQ7RWOA3FD3RSA", 20380821, 300))