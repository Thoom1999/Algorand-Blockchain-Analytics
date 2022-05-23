from utils import *

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
prettyPrint(getAssetTxInRange(start_block=18951072+100, end_block=18951072+250, asset_id=576840807))