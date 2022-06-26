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

# print(calculatePrice(10, 20, "a", "a"))
# print(getAssetTxInBlock(20821904, 444035862))
# print(getAlgoTransfer(20821904, "MAPEFN7K2M5Z4TPOVOXHVBTW2M46SQPROBLGYXAZ56K4SHTEUCOOZCMRZE", "2FJLXZ4QPMN5JFJ635B755Q4VH7AB4QCQA264GAEHJXLMCYEPLOUVODZLM"))
# print(getBlockInfos(20821904))

# print(getPoolAddr(444035862))

print(addLiquidityForFirstTime("UEMGT2KYO57HWZANRPAYZGECTS5TFT5KAJ3CVEN6QH6V3CLAL5UOV7Q4NQ", 581879854))
print(addLiquidityForFirstTime("UEMGT2KYO57HWZANRPAYZGECTS5TFT5KAJ3CVEN6QH6V3CLAL5UOV7Q4NQ", 581880471))